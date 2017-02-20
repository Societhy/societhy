from eventlet import event as g_event, greenpool, sleep as g_sleep

from signal import signal, SIGINT
from time import sleep
from sys import exit

from models.clients import eth_cli
from models.events import Event, EventQueue, LogEvent

class BlockchainWatcher:

    event_queue = None
    lock = None
    block_filter = None
    new_block_event = None
    thread = None
    is_running = None


    def __init__(self):
        self.newBlockFilter = eth_cli.eth_newBlockFilter()
        self.newBlockEvent = g_event.Event()
        self.newLogEvent = g_event.Event()
        self.lastEvent = None
        self.lastTx = None
        self.running = False
        self.event_queue = EventQueue()
        self.pool = greenpool.GreenPool(size=10)


    def run(self):
        signal(SIGINT, self.stopWithSignal)
        self.running = True
        self.pool.spawn(self.watch)

    def watch(self):
        if self.running:
            print('.', end='', flush=True)
            newBlocks = eth_cli.eth_getFilterChanges(self.newBlockFilter)
          
            for blockHash in newBlocks:
          
                block = eth_cli.eth_getBlockByHash(blockHash, True)
                self.lastTx = [tx.get('hash') for tx in block.get('transactions')]
                if self.newBlockEvent.ready():
                    self.newBlockEvent = g_event.Event()
                else:
                    self.newBlockEvent.send()
                print("new block %s with hash =" % block.get('number'), blockHash, "and tx =", self.lastTx)
          
                for event in self.event_queue.yieldEvents(block.get('transactions')):
                    if isinstance(event, LogEvent):
                        self.lastEvent = event
                        if self.newLogEvent.ready():
                            self.newLogEvent = g_event.Event()
                        else:
                            self.newLogEvent.send()
                    event.process()


            g_sleep(1)
            self.pool.spawn(self.watch)

    def pushEvent(self, event):
        # install a new filter in the node, push a new event in the queue with filter_id and user_id
        self.event_queue.append(event)

    def newBlockThen(self, function):
        self.newBlockEvent.wait()
        self.newBlockEvent = g_event.Event()
        function()

    def waitBlock(self, blockNumber=1):
        while blockNumber > 0:
            self.newBlockEvent.wait()
            self.newBlockEvent = g_event.Event()
            blockNumber -= 1

    def waitTx(self, tx_hash):
        print("waiting for tx %s..." % tx_hash)
        while True:
            self.newBlockEvent.wait()
            self.newBlockEvent = g_event.Event()
            if tx_hash in self.lastTx:
                return

    def waitEvent(self, event):
        print("waiting for event %s..." % event)
        while True:
            self.newLogEvent.wait()
            self.newLogEvent = g_event.Event()
            if self.lastEvent.name == event:
                self.lastEvent = None
                return

    def pause(self):
        print("BW PAUSED")
        self.running = False

    def resume(self):
        print("BW RESUMED")
        self.running = True
        self.watch()

    def stopWithSignal(self, signal, frame):
        print("BW EXITED AFTER SIGNAL")
        self.running = False
        self.pool.waitall()
        exit()

    def stop(self):
        print("BW EXITED")
        self.running = False
        self.pool.waitall()


blockchain_watcher = BlockchainWatcher()