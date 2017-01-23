import time
import json
import scrypt
from os import environ, listdir, path, remove
from base64 import b64decode, b64encode
from time import strftime, clock

from flask import session, request, Response

from models import users
from models.clients import eth_cli

from core.utils import normalizeAddress, fromWei

from rlp.utils import encode_hex

keyDirectory = environ.get('KEYS_DIRECTORY')

class KeyFormatError(Exception):
	pass

class KeyExistsError(Exception):
	pass

def genBaseKey(password):

	hashPassword = scrypt.hash(password, "rajoute du sel dans les carottes rapées")
	hashPassword = encode_hex(hashPassword).decode('utf-8')
	dirContent = listdir(keyDirectory)
	key = eth_cli.personal_newAccount(hashPassword)
	keyFile = list(set(listdir(keyDirectory)) - set(dirContent))[0]
	return {"address": key, "file": keyFile}

def genLinkedKey(user, password):

	def genKeyRemote(password):
		hashPassword = scrypt.hash(password, "rajoute du sel dans les carottes rapées")
		hashPassword = encode_hex(hashPassword).decode('utf-8')
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
	address = normalizeAddress(address, hexa=True)
	user.addKey(address, local_account=True, password_type="local", balance=fromWei(eth_cli.eth_getBalance(address)))
	return {
		"data": "OK",
		"status": 200
	}


def importNewKey(user, sourceKey):

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
		keyAlreadyExists(key.get('address'), user.get('eth').get('keys'))
		keyFilename = importKeyRemote(key.get('id'), sourceKey)
		key["address"] = normalizeAddress(key.get('address'), hexa=True)
		data = { "address" : key.get('address') }
		user.addKey(key.get('address'), local_account=False, password_type="local", balance=fromWei(eth_cli.eth_getBalance(key.get('address'))), keyfile=keyFilename)
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
