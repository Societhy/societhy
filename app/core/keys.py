import time
import json
import scrypt
from os import environ, listdir, path, remove
from base64 import b64decode, b64encode
from time import strftime, clock

from flask import session, request, Response

from models import users
from models.clients import eth_cli

from . import SALT_WALLET_PASSWORD
from core.utils import normalizeAddress, fromWei

from rlp.utils import encode_hex

"""
module that controls all the keys related features
"""

keyDirectory = environ.get('KEYS_DIRECTORY')

class KeyFormatError(Exception):
	pass

class KeyExistsError(Exception):
	pass

def genBaseKey(password):

	"""
	password : string for user's password
	password is hashed and a new ethereum account is created from it
	key file is returned alongside the address of the newly created account
	"""
	hashPassword = encode_hex(scrypt.hash(password, SALT_WALLET_PASSWORD)).decode('utf-8')
	dirContent = listdir(keyDirectory)
	key = eth_cli.personal_newAccount(hashPassword)
	keyFile = list(set(listdir(keyDirectory)) - set(dirContent))[0]
	return {"address": key, "file": keyFile}

def genLinkedKey(user, password):

	"""
	user : UserDoc
	password : string (non hashed)
	creates a new key and assigned it to a user
	"""

	def genKeyRemote(password):
		hashPassword = encode_hex(scrypt.hash(password, SALT_WALLET_PASSWORD)).decode('utf-8')
		dirContent = listdir(keyDirectory)
		key = eth_cli.personal_newAccount(hashPassword)
		keyFile = list(set(listdir(keyDirectory)) - set(dirContent))[0]
		return {"address": key, "file": keyFile}
	
	newKey = genKeyRemote(password)
	user.addKey(newKey.get('address'), local_account=False, password_type="local_hashed", balance=0, keyfile=newKey.get('file'))
	return {
		"data": newKey.get('address'),
		"status": 200
	}

def keyWasGenerated(user, address):
	"""
	user : UserDoc
	address : string of 20bytes of the address
	assignes an address, without the key file associated with it, to a user
	"""
	address = normalizeAddress(address, hexa=True)
	user.addKey(address, local_account=True, password_type="local", balance=fromWei(eth_cli.eth_getBalance(address)))
	return {
		"data": "OK",
		"status": 200
	}


def importNewKey(user, sourceKey):
	"""
	user : UserDoc
	sourceKey : json formatted array that contains the key file
	imports a key formatted as an array into a key file and assignes it to a user
	throws exceptions if key if has wrong format
	"""
	def isEthereumKey(keyFile):
		required_entries = set(["address", "crypto", "id", "version"])
		if not required_entries.issubset(set(keyFile.keys())):
			raise KeyFormatError

	def keyAlreadyExists(address, userExistingAddresses):
		if normalizeAddress(address, hexa=True) in userExistingAddresses.keys():
			raise KeyExistsError

	def importKeyRemote(keyId, sourceKey):
		keyFilename = "UTC--" + strftime("%Y-%m-%dT%H-%M-%S") + "." + str(clock())[2:] + "Z--" + keyId
		with open(path.join(keyDirectory, keyFilename), 'w') as f:
			f.write(sourceKey)
		return keyFilename

	status = 200
	sourceKey = sourceKey.read().decode('utf-8')

	try:
		key = json.loads(sourceKey)
		isEthereumKey(key)
		keyAlreadyExists(key.get('address'), user.get('eth').get('keys', {}))
		keyFilename = importKeyRemote(key.get('id'), sourceKey)
		key["address"] = normalizeAddress(key.get('address'), hexa=True)
		balance = fromWei(eth_cli.eth_getBalance(key.get('address')))
		data = { "address": key.get('address'), "balance": balance}
		user.addKey(key.get('address'), local_account=False, password_type="local", balance=balance, keyfile=keyFilename)
	except (json.JSONDecodeError, KeyFormatError):
		data = "key format not recognized"
		status = 400
	except (KeyExistsError):
		data = "trying to import an existing key"
		status = 400
	
	return {
		"data": data,
		"status": status
	}

def exportKey(user, address, delete=False):
	"""
	user : UserDoc
	address : 20bytes of the address
	delete : boolean for deleting the key from the user
	returns the given key and removes it if delete is set to True
	"""
	exportedKey = user.getKey(address)
	
	if exportedKey and delete and exportedKey.get('local_account') is True:
		user.removeKey(address, local_account=True)
		return {
			"data": None,
			"status": 200
		}

	elif exportedKey is not None:
		for keyFile in listdir(keyDirectory):
			if exportedKey.get('file') == keyFile:
				with open(path.join(keyDirectory, keyFile), 'r') as f:
					data = json.load(f)
					if delete is True:
						user.removeKey(address, local_account=False)
						remove(f.name)
					return {
						"data": data,
						"status": 200
					}

	return {
		"data": "Key does not exists",
		"status": 400
	}
