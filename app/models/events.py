from collections import deque
from .clients import eth_cli

# BASE CLASS FOR AN EVENT, EVERY EVENT CLASS MUST OVERRIDE IT
class Event:

	def __init__(self, tx_hash=None, users=[], callback=None):
		self.tx_hash = tx_hash
		self.users = users
		self.callback = callback

	def process(self):
		print("PROCESSING EVENT", self.tx_hash)
		self.callback(self.tx)


# EVENT CLASS FOR CONTRACT CREATION
class ContractCreationEvent(Event):

	def process(self):
		print("PROCESSING EVENT", self.tx_hash)
		self.tx_receipt = eth_cli.eth_getTransactionReceipt(self.tx_hash)
		self.callback(self.tx_receipt)


class LogEvent(Event):
	pass

# SAFE QUEUE FOR EVENTS
class EventQueue(deque):

	def yieldEvents(self, transactions):
		ret = list()
		for tx in transactions:
			for event in list(self):
				if event.tx_hash == tx.get('hash'):
					event.tx = tx
					yield event
					self.remove(event)