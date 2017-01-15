from collections import deque
from .clients import eth_cli

# BASE CLASS FOR AN EVENT, EVERY EVENT CLASS MUST OVERRIDE IT
class Event:

	filter_params = None
	filter_id = None
	tx_hash = None
	users = None
	callback = None

	def __init__(self, tx_hash=None, users=[], callbacks=None):
		self.tx_hash = tx_hash
		self.users = users
		if isinstance(callbacks, list):
			self.callbacks = callbacks
		elif callable(callbacks):
			self.callbacks = [callbacks]

	def happened(self):
		return False

	def process(self):
		print("PROCESSING EVENT", self.tx_hash)
		for cb in self.callbacks:
			cb()


# EVENT CLASS FOR CONTRACT CREATION
class ContractCreationEvent(Event):

	def process(self):
		print("PROCESSING EVENT", self.tx_hash)
		self.tx_receipt = eth_cli.eth_getTransactionReceipt(self.tx_hash)
		for cb in self.callbacks:
			cb(self.tx_receipt)


class LogEvent(Event):

	def __init__(self, name, contract_address, topics=None, users=[], callbacks=None):
		super().__init__(users=users, callbacks=callbacks)
		self.logs = None
		self.name = name
		self.filter_id = eth_cli.eth_newFilter(address=contract_address, topics=topics)

	def process(self):
		print("PROCESSING EVENT", self.name)
		for cb in self.callbacks:
			cb(self.logs)

# SAFE QUEUE FOR EVENTS
class EventQueue(deque):

	lock = None

	def yieldEvents(self, transactions):
		ret = list()
		# YIELD TRANSACTION EVENTS
		for tx in transactions:
			for event in [ev for ev in self if isinstance(ev, ContractCreationEvent)]:
				if event.tx_hash == tx.get('hash'):
					event.tx = tx
					yield event
					self.remove(event)

		# YIELD LOG EVENTS
		for event in [ev for ev in self if isinstance(ev, LogEvent)]:
			logs = eth_cli.eth_getFilterChanges(event.filter_id)
			if logs:
				event.logs = logs
				yield event
				self.remove(event)
