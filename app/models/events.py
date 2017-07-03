from collections import deque

from core.utils import to32bytes
from rlp.utils import decode_hex
from sha3 import keccak_256

from .clients import eth_cli, socketio

"""
this module defines classes that represent event fired by the smart contracts. They are registred as requests are made by users that requires a transaction on the blockchain.
"""

def makeTopics(signature, *args):
	
	ret = list()
	if signature:
		signature = to32bytes(keccak_256(signature.encode('utf-8')).hexdigest())
	ret.append(signature)
	for arg in args:
		ret.append(to32bytes(arg))
	return ret

def computeEventTypes(event_name, abi):
	event_types = list()
	for elem in abi:
		if elem.get('type') == 'event' and elem.get('name') == event_name:
			for _input in elem.get('inputs'):
				event_types.append(_input.get('type'))
			break
	return event_types


class Event:

	"""
	 BASE CLASS FOR AN EVENT, EVERY EVENT CLASS MUST OVERRIDE IT
	 Interface that defines 2 main methods, triggering the callback and sending the asynchronous responses through socketio to notified users.
	"""

	filter_params = None
	filter_id = None
	tx_hash = None
	users = None
	callback = None
	callback_data = None
	mail = None
	name = "defaultEvent"
	notified = list()

	def __init__(self, tx_hash=None, users=[], callbacks=None, callback_data=None, mail=None):
		self.tx_hash = tx_hash
		self.callback_data = callback_data

		if isinstance(users, list):
			self.users = [user if isinstance(user, str) else user.get('socketid') for user in users]
		elif isinstance(users, str):
			self.users = [users]
		else:
			self.users = [users.get('socketid')] if users.get('socketid') is not None else None

		if mail:
			self.mail = mail
		if isinstance(callbacks, list):
			self.callbacks = callbacks
		elif callable(callbacks):
			self.callbacks = [callbacks]

	def notifyUsers(self, data=None):
		"""
		For each user registered on the event, send a socketio message for notifying the transaction and its results
		"""
		if self.users:
			if data is not None:
				for user in list(self.users):
					payload = {"event": self.name, "data": data}
					print("EMITTING", "payload", "to", user)
					socketio.emit('txResult', payload, room=user)
					self.users.remove(user)


	def happened(self):
		return False

	def process(self):
		"""
		Retrieves data from the transaction receipt and triggers callback(s)
		"""
		self.tx_receipt = eth_cli.eth_getTransactionReceipt(self.tx_hash)
		print("PROCESSING EVENT", self.tx_hash, "--------------", self.tx_receipt)
		for cb in self.callbacks:
			notifyUsers(self.users, cb())
		return self


# EVENT CLASS FOR CONTRACT CREATION
class ContractCreationEvent(Event):

	"""
	Event specific to contract deployment on the blockchain
	"""

	name = "contractCreation"

	def process(self):
		print("PROCESSING EVENT", self.tx_hash)
		self.tx_receipt = eth_cli.eth_getTransactionReceipt(self.tx_hash)
		for cb in self.callbacks:
			self.notifyUsers(cb(self.tx_receipt, self.callback_data))
		return self

class LogEvent(Event):

	"""
	Event specific to log events (see further documentation) contained in the state of the blockchain.
	"""
	def __init__(self, name, tx_hash, contract_address, topics=None, users=[], callbacks=None, callback_data=None, event_abi=None, mail=None):
		super().__init__(users=users, tx_hash=tx_hash, callbacks=callbacks, mail=mail)
		self.logs = None
		self.topics = topics
		self.name = name
		self.contract_address = contract_address
		self.event_abi = event_abi
		self.callback_data = callback_data

	def process(self):
		"""
		When processing a log event, the data contained in the payload must be decoded and formatted
		The data is then transmitted in the callbacks.
		"""
		print("PROCESSING EVENT", self.name)
		tx_receipt = eth_cli.eth_getTransactionReceipt(self.tx_hash)
		self.logs = tx_receipt.get('logs')
		if self.event_abi and len(self.logs) >= 1:
			raw_data = self.logs[0].get('data')[2:]
			i = 32
			decoded_data = list()
			while i <= len(raw_data):
				try:
					decoded_data.append(decode_hex(raw_data[i-32:i]).decode("ascii"))
				except:
					decoded_data.append(decode_hex(raw_data[i-32:i]))
				i += 32
			self.logs[0]["decoded_data"] = [line for line in [line.strip('\x00').strip() for line in decoded_data] if len(line) > 1]
		if self.mail:
			for user in self.mail['users']:
				from models.notification import notifyToOne
				notifyToOne(self.mail['sender'], user, 'NewMember', self.mail['subject'])
		for cb in self.callbacks:
			self.notifyUsers(cb(self.logs, self.callback_data))
		return self

# SAFE QUEUE FOR EVENTS
class EventQueue(deque):

	"""
	Overrides a deque and stores all the event registered by the models.
	"""
	def yieldEvents(self, transactions):
		"""
		transactions : list of dict of each new transaction
		Compares the transaction currently being stored to those contained in the new block
		"""
		ret = list()
		for tx in transactions:
			for event in list(self):
				if event.tx_hash == tx.get('hash'):
					event.tx = tx
					yield event
					self.remove(event)


