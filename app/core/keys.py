import time
import json
import scrypt
from os import environ, listdir, path, remove
from base64 import b64decode, b64encode
from time import strftime, clock

from flask import session, request, Response

from models import users
from models.db import eth_cli

from core.utils import normalize_address, fromWei

from rlp.utils import encode_hex

keyDirectory = environ.get('KEYS_DIRECTORY')

class KeyFormatError(Exception):
	pass

class KeyExistsError(Exception):
	pass

def gen_base_key():

	hashPassword = scrypt.hash("societhy", "rajoute du sel dans les carottes rapées")
	hashPassword = encode_hex(hashPassword).decode('utf-8')
	dirContent = listdir(keyDirectory)
	key = eth_cli.personal_newAccount(hashPassword)
	keyFile = list(set(listdir(keyDirectory)) - set(dirContent))[0]
	return {"address": key, "file": keyFile}

def gen_linked_key(user, password):

	def gen_key_remote(password):
		hashPassword = scrypt.hash(password, "je trouve que les carottes ne sont pas assez salées")
		hashPassword = encode_hex(hashPassword).decode('utf-8')
		dirContent = listdir(keyDirectory)
		key = eth_cli.personal_newAccount(hashPassword)
		keyFile = list(set(listdir(keyDirectory)) - set(dirContent))[0]
		return {"address": key, "file": keyFile}
	
	newKey = gen_key_remote(password)
	user.add_key(newKey.get('address'), local=False, balance=0, file=newKey.get('file'))
	return {
		"data": newKey.get('address'),
		"status": 200
	}

def key_was_generated(user, address):
	address = normalize_address(address, hexa=True)
	user.add_key(address, local=True, balance=fromWei(eth_cli.eth_getBalance(address)))
	return {
		"data": "OK",
		"status": 200
	}


def import_new_key(user, sourceKey):

	def is_ethereum_key(keyFile):
		required_entries = set(["address", "crypto", "id", "version"])
		if not required_entries.issubset(set(keyFile.keys())):
			raise KeyFormatError

	def key_already_exists(address, userExistingAddresses):
		if normalize_address(address, hexa=True) in userExistingAddresses.keys():
			raise KeyExistsError

	def import_key_remote(keyId, sourceKey):
		keyFilename = "UTC--" + strftime("%Y-%m-%dT%H-%M-%S") + "." + str(clock())[2:] + "Z--" + keyId
		with open(path.join(keyDirectory, keyFilename), 'w') as f:
			f.write(sourceKey)
		return keyFilename

	status = 200
	sourceKey = sourceKey.read().decode('utf-8')

	try:
		key = json.loads(sourceKey)
		is_ethereum_key(key)
		key_already_exists(key.get('address'), user.get('eth').get('keys'))
		keyFilename = import_key_remote(key.get('id'), sourceKey)
		key["address"] = normalize_address(key.get('address'), hexa=True)
		data = { "address" : key.get('address') }
		user.add_key(key.get('address'), local=False, balance=fromWei(eth_cli.eth_getBalance(key.get('address'))), file=keyFilename)
	except (json.JSONDecodeError, KeyFormatError):
		data = "key format nor recognized"
		status = 400
	except (KeyExistsError):
		data = "trying to import an existing key"
		status = 400
	
	return {
		"data": data,
		"status": status
	}

def export_key(user, address, delete=False):
	exportedKey = user.get_key(address)
	
	if delete and exportedKey.get('local') is True:
		user.remove_key(address, local=True)
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
						user.remove_key(address, local=False)
						remove(f.name)
					return {
						"data": data,
						"status": 200
					}

	return {
		"data": "Key does not exists",
		"status": 400
	}
