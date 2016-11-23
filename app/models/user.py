from bson.objectid import ObjectId

from mongokat import Collection, Document

from .db import client, eth_cli
from ethjsonrpc import wei_to_ether

class UserDocument(Document):
	
	def save_partial(self, data=None, allow_protected_fields=False, **kwargs):
		if self['_id'] is not None:
			self['_id'] = ObjectId(self.get('_id')) if type(self.get('_id')) is str else self['_id']
		super().save_partial(data, allow_protected_fields, **kwargs)

	def add_key(self, key, local, balance=0):
		if self.get('eth').get('mainKey') is None:
			self["eth"]["mainKey"] = key

		self["eth"]["keys"][key] = {
			"balance": balance,
			"local": local,
			"address": key
		 }
		self.save_partial()

	def remove_key(self, key, local):
		for publicKey in self["eth"]["keys"].keys():
			if publicKey == key:
				del self["eth"]["keys"][publicKey]
				if self["eth"]["mainKey"] == key:
					self["eth"]["mainKey"] = None
				self.save_partial()
				return

	def get_key(self, publicKey=None):
		if publicKey is None:
			return self.get('eth').get('mainKey')
		else:
			for key in self.get('eth').get('keys').keys():
				if key == publicKey:
					return self.get('eth').get('keys').get(key) 
			return None
					
	def refresh_balance(self, address=None):
		address = address or self.get('eth').get('mainKey')
		if address:
			balance = eth_cli.eth_getBalance(address)
			self['eth']['keys'][address]["balance"] = balance
			self.save_partial()
			return wei_to_ether(balance)
		return None


class UserCollection(Collection):
	user_info = [
		"_id",
		"name",
		"address",
		"eth",
		"eth.mainKey",
		"eth.keys",
		"email",
		"gender",
		"firstname",
		"lastname",
		"city"
	]

	document_class = UserDocument

users = UserCollection(collection=client.main.users)
