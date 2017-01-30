import threading

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
        self.newBlockEvent = threading.Event()
        self.newLogEvent = threading.Event()
        self.lastEvent = None
        self.lastTx = None
        self.running = False
        self.lock = threading.Lock()
        self.event_queue = EventQueue()
        self.thread = threading.Thread(target=self.watch)


    def run(self):
        signal(SIGINT, self.stopWithSignal)
        self.running = True
        self.thread.start()

    def watch(self):
        if self.running:
            print('.', end='', flush=True)
            newBlocks = eth_cli.eth_getFilterChanges(self.newBlockFilter)
          
            for blockHash in newBlocks:
          
                block = eth_cli.eth_getBlockByHash(blockHash, True)
                print("new block %s with hash =" % block.get('number'), blockHash, "and tx =", self.lastTx)
          
                for event in self.event_queue.yieldEvents(block.get('transactions')):
                    if isinstance(event, LogEvent):
                        self.lastEvent = event
                        self.newLogEvent.set()
                        self.newLogEvent.clear()
                    event.process()

                self.lastTx = [tx.get('hash') for tx in block.get('transactions')]
                self.newBlockEvent.set()
                self.newBlockEvent.clear()

            threading.Timer(1, self.watch).start()

    def pushEvent(self, event):
        # install a new filter in the node, push a new event in the queue with filter_id and user_id
        self.event_queue.append(event)

    def newBlockThen(self, function):
        self.newBlockEvent.wait()
        function()

    def waitBlock(self, blockNumber=1):
        while blockNumber > 0:
            self.newBlockEvent.wait()
            blockNumber -= 1

    def waitTx(self, tx_hash):
        print("waiting for tx %s..." % tx_hash)
        while True:
            self.newBlockEvent.wait()
            if tx_hash in self.lastTx:
                return

    def waitEvent(self, event):
        print("waiting for event %s..." % event)
        while True:
            self.newLogEvent.wait()
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
        self.thread.join()
        exit()

    def stop(self):
        print("BW EXITED")
        self.running = False
        self.thread.join()


blockchain_watcher = BlockchainWatcher()