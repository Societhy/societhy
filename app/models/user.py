from bson.objectid import ObjectId

from mongokat import Collection, Document

from .db import client

class UserDocument(Document):
	
	def save_partial(self, data=None, allow_protected_fields=False, **kwargs):
		if self['_id'] is not None:
			self['_id'] = ObjectId(self.get('_id')) if type(self.get('_id')) is str else self['_id']
		super().save_partial(data, allow_protected_fields, **kwargs)

	def add_key(self, key, local):
		if self.get('eth').get('mainKey') is None:
			self["eth"]["mainKey"] = key

		if self.get('eth').get('keys') is not None:
			self["eth"]["keys"].append({
				"address": key,
				"local": local
			 })

		else:
			self["eth"]["keys"] = [{
				"address": key,
				"local": local
			 }]
		self.save_partial()

	def remove_key(self, key, local):
		for publicKey in self["eth"]["keys"]:
			if publicKey.get('address') == key:
				self["eth"]["keys"].remove(publicKey)
				self.save_partial()

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

users = UserCollection(collection=client.main.users)
