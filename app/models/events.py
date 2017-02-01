from os import environ as env
from sha3 import keccak_256

from collections import deque

from .clients import eth_cli

from core.utils import to32bytes
from core.chat import socketio

# BASE CLASS FOR AN EVENT, EVERY EVENT CLASS MUST OVERRIDE IT

def makeTopics(signature, *args):
	
	ret = list()
	if signature:
		signature = to32bytes(keccak_256(signature.encode('utf-8')).hexdigest())
	ret.append(signature)
	for arg in args:
		ret.append(to32bytes(arg))
	return ret

class Event:

	filter_params = None
	filter_id = None
	tx_hash = None
	users = None
	callback = None
	name = "defaultEvent"

	def __init__(self, tx_hash=None, users=[], callbacks=None):
		self.tx_hash = tx_hash
		self.users = users
		if isinstance(callbacks, list):
			self.callbacks = callbacks
		elif callable(callbacks):
			self.callbacks = [callbacks]

	def notifyUsers(self, data=None):
		if self.users:
			for user in self.users:
				payload = {"event": self.name, "data": data}
				socketio.emit('txResult', payload, room=user)

	def happened(self):
		return False

	def process(self):
		self.tx_receipt = eth_cli.eth_getTransactionReceipt(self.tx_hash)
		print("PROCESSING EVENT", self.tx_hash, "--------------", self.tx_receipt)
		for cb in self.callbacks:
			notifyUsers(self.users, cb())


# EVENT CLASS FOR CONTRACT CREATION
class ContractCreationEvent(Event):

	name = "contractCreation"

	def process(self):
		print("PROCESSING EVENT", self.tx_hash)
		self.tx_receipt = eth_cli.eth_getTransactionReceipt(self.tx_hash)
		for cb in self.callbacks:
			self.notifyUsers(cb(self.tx_receipt))

class LogEvent(Event):

	def __init__(self, name, tx_hash, contract_address, topics=None, users=[], callbacks=None):
		super().__init__(users=users, tx_hash=tx_hash, callbacks=callbacks)
		self.logs = None
		self.topics = topics
		self.name = name
		self.contract_address = contract_address

	def process(self):
		print("PROCESSING EVENT", self.name)
		tx_receipt = eth_cli.eth_getTransactionReceipt(self.tx_hash)
		self.logs = tx_receipt.get('logs')
		for cb in self.callbacks:
			self.notifyUsers(cb(self.logs))

# SAFE QUEUE FOR EVENTS
class EventQueue(deque):

	lock = None

	def yieldEvents(self, transactions):
		ret = list()
		# YIELD TRANSACTION EVENTS
		for tx in transactions:
			for event in list(self):
				if event.tx_hash == tx.get('hash'):
					event.tx = tx
					yield event
					self.remove(event)
