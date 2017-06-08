"""
This class is an abstraction of a greenthread co-routine. It also contains a shared container where events can be stored and being "watched on".
Every second, the function watch() is ran, new events are retrieved from the blockchain and compared to the registered events. A match triggers the callback stored into the event object (see Event class)
Some functions allow to control the process of the transactions and wait for events.
"""

from eventlet import event as g_event, greenthread, sleep as g_sleep

from signal import signal, SIGINT
from time import sleep
from sys import exit

from models.clients import eth_cli
from models.events import Event, EventQueue, LogEvent

class BlockchainWatcher:


    """
    eventQueue : shared queue where the current events are stored
    newBlockFilter : ethereum event that retrieves new block as they are mined
    newBlockEvent : eventlet event triggered when a new block is mined
    currentWorker : greenthread associated with the routine
    running : boolean controlling the status of the watcher

    """
    eventQueue = None
    newBlockEvent = None
    currentWorker = None
    running = None


    def __init__(self):

        """
        Initialize each member with its starting values
        """

        self.newBlockFilter = eth_cli.eth_newBlockFilter()
        self.newBlockEvent = g_event.Event()
        self.newLogEvent = g_event.Event()
        self.lastEvent = None
        self.lastTx = None
        self.waiting = False
        self.running = False
        self.eventQueue = EventQueue()

    def run(self):

        """
        Sets the status to running and launch a new greenthread assigned with the routine 'watch'
        """
        self.running = True
        self.currentWorker = greenthread.spawn(self.watch)

    def watch(self):
        """
        If the status is set to running, try to retrieve new blocks from the blockchain through the ethjsonrpc API
        For each new block, a newBlockEvent is triggered and all the transactions are compared to the ones stored in memory pf the eventQueue. If a match occures, a NewLogEvent is triggered and the callback previously registered inside the event is called.
        The callbacks are used to update the models accordingly to the new data retrieved from the transactions in the new blocks.
        Finally an other routine is scheduled for the next second.
        """
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
          
                for event in self.eventQueue.yieldEvents(block.get('transactions')):
                    if isinstance(event, LogEvent):
                        self.lastEvent = event
                        if self.newLogEvent.ready():
                            self.newLogEvent = g_event.Event()
                        else:
                            self.newLogEvent.send()
                    event.process()

            self.currentWorker = greenthread.spawn_after(1, self.watch)

    def pushEvent(self, event):
        """
        event : models.Event and child classes
        push a new event in the queue with filter_id and user_id
        """
        self.eventQueue.append(event)

    def newBlockThen(self, function):
        """
        function : callback to be called
        waits for the next block then triggers the callback 'function'
        """
        self.newBlockEvent.wait()
        self.newBlockEvent = g_event.Event()
        function()

    def waitBlock(self, blockNumber=1):
        """
        blockNumber : integer / number of block that need to be mined 
        waits for a given number of blocks before triggering a newBlockEvent
        """
        while blockNumber > 0:
            self.newBlockEvent.wait()
            self.newBlockEvent = g_event.Event()
            blockNumber -= 1

    def waitTx(self, tx_hash):
        """
        tx_hash : string / transaction hash to be waited for
        Waits for a given transaction
        """
        print("waiting for tx %s..." % tx_hash)
        while True:
            self.newBlockEvent.wait()
            self.newBlockEvent = g_event.Event()
            if tx_hash in self.lastTx:
                return

    def waitEvent(self, event):
        """
        event : models.Event  / event to be waited for
        Waits for a given event
        """
        print("waiting for event %s..." % event)
        while True:
            self.newLogEvent.wait()
            self.newLogEvent = g_event.Event()
            if self.lastEvent.name == event:
                self.lastEvent = None
                return

    def pause(self):
        """
        Breaks the routine by setting the status to not running
        """
        print("BW PAUSED")
        self.running = False

    def resume(self):
        """
        Relaunches the routine
        """
        print("BW RESUMED")
        self.running = True
        self.watch()

    def stopWithSignal(self, signal, frame):
        """
        Shut down the thred when catching a signal ctrl+c
        """
        print("BW EXITED AFTER SIGNAL (please ctrl+C an other time to terminate and flush session)")
        self.running = False
        self.currentWorker.cancel()

    def stop(self):
        """
        Stops the routine
        """
        print("BW EXITED")
        self.running = False


blockchain_watcher = BlockchainWatcher()