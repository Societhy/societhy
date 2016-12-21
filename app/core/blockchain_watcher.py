import threading

from signal import signal, SIGINT
from time import sleep
from sys import exit

from models.clients import eth_cli
from models.events import Event, EventQueue

class BlockchainWatcher:

    def __init__(self):
        self.blockFilter = eth_cli.eth_newBlockFilter()
        self.newBlockEvent = threading.Event()
        self.running = False
        self.lock = threading.Lock()
        self.event_queue = EventQueue()

    def run(self):
        signal(SIGINT, self.stop_with_signal)
        self.running = True
        self.thread = threading.Thread(target=self.watch)
        self.thread.start()

    def watch(self):
        if self.running:
          
            newBlocks = eth_cli.eth_getFilterChanges(self.blockFilter)
          
            for blockHash in newBlocks:
          
                block = eth_cli.eth_getBlockByHash(blockHash, True)
                self.last_tx = [tx.get('hash') for tx in block.get('transactions')]
                print("new block %s with hash =" % block.get('number'), blockHash, "and tx =", self.last_tx)
          
                for event in self.event_queue.yieldEvents(block.get('transactions')):
                    event.process()

                self.newBlockEvent.set()
                self.newBlockEvent.clear()

            threading.Timer(1, self.watch).start()

    def push_event(self, event):
        # install a new filter in the node, push a new event in the queue with filter_id and user_id
        self.event_queue.append(event)

    def newBlock_then(self, function):
        self.newBlockEvent.wait()
        function()

    def waitBlock(self, blockNumber=1):
        while blockNumber > 0:
            self.newBlockEvent.wait()
            blockNumber -= 1

    def waitTx(self, tx_hash):
        while True:
            self.newBlockEvent.wait()
            if tx_hash in self.last_tx:
                return

    def pause(self):
        print("BW PAUSED")
        self.running = False

    def resume(self):
        print("BW RESUMED")
        self.running = True
        self.watch()

    def stop_with_signal(self, signal, frame):
        print("BW EXITED AFTER SIGNAL")
        self.running = False
        self.thread.join()
        exit()

    def stop(self):
        print("BW EXITED")
        self.running = False
        self.thread.join()


blockchain_watcher = BlockchainWatcher()