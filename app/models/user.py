import scrypt

from flask import session
from bson.objectid import ObjectId
from mongokat import Collection, Document
from rlp.utils import encode_hex

from .clients import client, eth_cli

from core import SALT_WALLET_PASSWORD
from core.utils import fromWei

class UserDocument(Document):

	def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None, session=None):
		super().__init__(doc, users, fetched_fields, gen_skel)
		self.session_token = session

	def needsReloading(self):
		if self.session_token:
			session[self.session_token]["needs_reloading"] = True

	def reload(self):
		if self['_id'] and type(self['_id']) is str:
			self['_id'] = ObjectId(self.get('_id')) if type(self.get('_id')) is str else self['_id']
		super().reload()

	def save_partial(self, data=None, allow_protected_fields=False, **kwargs):
		if self['_id'] and type(self['_id']) is str:
			self['_id'] = ObjectId(self.get('_id')) if type(self.get('_id')) is str else self['_id']
		super().save_partial(data, allow_protected_fields, **kwargs)

	# CALLBACKS FOR UPDATE

	def joinedOrga(self, logs):
		if len(logs) == 1 and logs[0].get('address') is not None:
			address = logs[0].get('address')
			orga = organizations.find_one({"address": address})
			if orga and orga.public() not in self["organizations"]:
				self["organizations"].append(orga.public())
				self.save_partial();
			else:
				return False
		return None

	def leftOrga(self, logs):
		if len(logs) == 1 and logs[0].get('address') is not None:
			address = logs[0].get('address')
			orga = organizations.find_one({"address": address})
			if orga and orga.public() in self["organizations"]:
				self["organizations"].remove(orga.public())
				self.save_partial()
			else:
				return False
		return None

	def madeDonation(self, logs):
		print("USER MADE DONATION", logs)
		return None

	# KEY MANAGEMENT

	def unlockAccount(self, password=None):
		if not self.get('account'):
			return False
		elif self["password_type"] == "remote_hashed":
			password = self.hashPassword(self['password'])
		elif self["password_type"] == "local_hashed" and password is not None:
			password = self.hashPassword(password)
		elif self["password_type"] == "local" and password is not None:
			password = password

		if password is not None:
			return eth_cli.personal_unlockAccount(self["account"], password)
		else:
			return False

	def hashPassword(self, password):
		return encode_hex(scrypt.hash(password, SALT_WALLET_PASSWORD)).decode('utf-8')

	def populateKey(self):
		from core.keys import genBaseKey
		newKey = genBaseKey(self["password"])
		if newKey:
			self.addKey(newKey.get('address'), local_account=False, password_type="remote_hashed", keyfile=newKey.get('file'))
		else:
			self["account"] = None
			self["eth"] = {"keys": {}}
		self.save_partial()

	def generatePersonalDataFromSocial(self):
		fields = {"firstname", "lastname", "pictureURL", "email", "company"}
		if 'social' in self:
			for socialProvider, socialData in self['social'].items():
				for key, value in socialData.items():
					if key in fields and key not in self:
						self[key] = value
		self.save_partial()

	def setDefaultKey(self, account):
		if account in self.get('eth').get('keys'):
			defaultKey = self["eth"]["keys"][account]
			self["account"] = defaultKey.get('address')
			self["local_account"] = defaultKey.get('local_account')
			self["password_type"] = defaultKey.get('password_type')
			self.save_partial()

	def addKey(self, account, local_account, password_type, balance=0, keyfile=None):
		if self.get('account') is None:
			self["account"] = account
			self["local_account"] = local_account
			self["password_type"] = password_type

		if not self.get('eth'):
			self["eth"] = {"keys":{}}

		self["eth"]["keys"][account] = {
			"balance": balance,
			"local_account": local_account,
			"password_type": password_type,
			"address": account,
			"file": keyfile
		 }
		self.save_partial()

	def removeKey(self, key, local_account):
		for publicKey in self["eth"]["keys"].keys():
			if publicKey == key:
				del self["eth"]["keys"][publicKey]
				if self["account"] == key:
					self["account"] = None
					self["local_account"] = None
					self["password_type"] = None
				self.save_partial()
				return

	def getKey(self, publicKey=None):
		if publicKey is None:
			return self.get('account')
		else:
			for key in self.get('eth').get('keys').keys():
				if key == publicKey:
					return self.get('eth').get('keys').get(key)
			return None

	def refreshBalance(self, address=None):
		address = address or self.get('account')
		if address:
			balance = fromWei(eth_cli.eth_getBalance(address))
			if address in self['eth']['keys']:
				self['eth']['keys'][address]["balance"] = balance
				self.save_partial()
			return balance
		return None

	def public(self):
		return {
			key: self.get(key)for key in self if key in users.public_info
		}

	def delete(self):
		return self.mongokat_collection.remove({"_id": ObjectId(self.get('_id'))})


class UserCollection(Collection):
	user_info = [
		"_id",
		"name",
		"address",
		"account",
		"local_account",
		"password_type",
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
		"organizations"
	]

	structure = {
		"name": str,
		"address": str,
		"account": str,
		"local_account": str,
		"password_type": str,
		"eth": dict,
		"email": str,
		"gender": str,
		"firstname": str,
		"lastname": str,
		"city": str,
        "contact_list": list,
        "organizations": list
	}

	document_class = UserDocument

users = UserCollection(collection=client.main.users)
from models.organization import organizations

