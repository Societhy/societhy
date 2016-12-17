import threading

from signal import signal, SIGINT
from time import sleep
from sys import exit
from collections import deque

from models.db import eth_cli
from models.events import Event

class BlockchainWatcher:

    def __init__(self):
        self.blockFilter = eth_cli.eth_newBlockFilter()
        self.newBlockEvent = threading.Event()
        self.running = True
        self.lock = threading.Lock()
        self.event_queue = deque()

    def run(self):
        signal(SIGINT, self.stop_with_signal)
        self.thread = threading.Thread(target=self.watch)
        self.thread.start()

    def watch(self):
        if self.running:
            newBlock = eth_cli.eth_getFilterChanges(self.blockFilter)
            if len(newBlock):
                print(newBlock)
                self.newBlockEvent.set()
                self.newBlockEvent.clear()
            print(eth_cli.eth_blockNumber())
            threading.Timer(1, self.watch).start()

    def push_event(self, event):
        self.event_queue.append(event)

    def newBlock_then(self, function):
        self.newBlockEvent.wait()
        function()

    def waitBlock(self, blockNumber=1):
        while blockNumber > 0:
            self.newBlockEvent.wait()
            blockNumber -= 1

    def stop_with_signal(self, signal, frame):
        self.running = False
        self.thread.join()
        print("exited")
        exit()

    def stop(self):
        self.running = False
        self.thread.join()
        print("exited")


blockchain_watcher = BlockchainWatcher()