from bson.objectid import ObjectId

from mongokat import Collection, Document
from .clients import client, eth_cli
from ethjsonrpc import wei_to_ether

class UserDocument(Document):

	def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None):
		super().__init__(doc, users, fetched_fields, gen_skel)

	def save_partial(self, data=None, allow_protected_fields=False, **kwargs):
		if self['_id'] is not None:
			self['_id'] = ObjectId(self.get('_id')) if type(self.get('_id')) is str else self['_id']
		super().save_partial(data, allow_protected_fields, **kwargs)

	# CALLBACKS FOR UPDATE

	def joinedOrga(self, logs):
		print("USER JOINED ORGA", logs)

	def leftOrga(self, logs):
		print("USER LEFT ORGA", logs)

	def madeDonation(self, logs):
		print("USER MADE DONATION", logs)
	# KEY MANAGEMENT

	def populate_key(self):
		from core.keys import gen_base_key
		newKey = gen_base_key()
		if newKey:
			self.add_key(newKey.get('address'), local=False, keyfile=newKey.get('file'))
		else:
			self["account"] = None
			self["eth"] = {"keys": {}}
			self.save_partial()

	def generatePersonalDataFromSocial(self):
		fields = {"firstname", "lastname", "pictureURL", "email", "company"}
		if 'social' in self:
			for socialProvider, socialData in self['social'].items():
				for key, value in socialData.items():
					# print(key)
					# print(value)
					if key in fields and key not in self:
						self[key] = value
		self.save_partial()

	def add_key(self, account, local, balance=0, keyfile=None):
		if self.get('account') is None:
			self["account"] = account
			self["local_account"] = local

		if not self.get('eth'):
			self["eth"] = {"keys":{}}

		self["eth"]["keys"][account] = {
			"balance": balance,
			"local": local,
			"address": account,
			"file": keyfile
		 }
		self.save_partial()

	def remove_key(self, key, local):
		for publicKey in self["eth"]["keys"].keys():
			if publicKey == key:
				del self["eth"]["keys"][publicKey]
				if self["account"] == key:
					self["account"] = None
					self["local_account"] = False
				self.save_partial()
				return

	def get_key(self, publicKey=None):
		if publicKey is None:
			return self.get('account')
		else:
			for key in self.get('eth').get('keys').keys():
				if key == publicKey:
					return self.get('eth').get('keys').get(key)
			return None

	def refresh_balance(self, address=None):
		address = address or self.get('account')
		if address:
			balance = wei_to_ether(eth_cli.eth_getBalance(address))
			if address in self['eth']['keys']:
				self['eth']['keys'][address]["balance"] = balance
				self.save_partial()
			return balance
		return None


class UserCollection(Collection):
	user_info = [
		"_id",
		"name",
		"address",
		"account",
		"local_account"
		"eth",
		"eth.keys",
		"email",
		"gender",
		"firstname",
		"lastname",
		"city",
        "contact_list",
        "organizations"
	]

	public_info = [
		"_id",
		"name",
		"account",
		"firstname",
		"lastname",
	]

	document_class = UserDocument

users = UserCollection(collection=client.main.users)
