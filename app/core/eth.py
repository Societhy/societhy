import time
import json
import scrypt
from os import environ, listdir, path, remove
from base64 import b64decode, b64encode
from time import strftime, clock

from flask import session, request, Response

from models import users
from models.db import eth_cli

from rlp.utils import encode_hex

class KeyFormatError(Exception):
	pass

class KeyExistsError(Exception):
	pass

def gen_linked_key(user, password):

	def gen_key_remote(password):
		hashPassword = scrypt.hash(password, "je trouve que les carottes ne sont pas assez salées")
		hashPassword = encode_hex(hashPassword).decode('utf-8')
		key = eth_cli.personal_newAccount(hashPassword)

		if key.startswith('0x'):
			key = key[2:]
		return key
	
	newKey = gen_key_remote(password)
	user.add_key(newKey, local=False)
	return {
		"data": newKey,
		"status": 200
	}

def key_was_generated(user, address):
	user.add_key(address, local=True)
	return {
		"data": "OK",
		"status": 200
	}


def import_new_key(user, sourceKey):

	def is_ethereum_key(keyFile):
		required_entries = set(["address", "crypto", "id", "version"])
		if not required_entries.issubset(set(keyFile.keys())):
			raise KeyFormatError

	def key_already_exists(address):
		keyDirectory = environ.get('KEYS_DIRECTORY')
		for keyFile in listdir(keyDirectory):
			if address in keyFile:
				raise KeyExistsError

	def import_key_remote(address, sourceKey):
		keyDirectory = environ.get('KEYS_DIRECTORY')
		keyFilename = "UTC--" + strftime("%Y-%m-%dT%H-%M-%S") + "." + str(clock())[2:] + "Z--" + address
		with open(path.join(keyDirectory, keyFilename), 'w') as f:
			f.write(sourceKey)

	status = 200
	sourceKey = sourceKey.read().decode('utf-8')

	try:
		key = json.loads(sourceKey)
		is_ethereum_key(key)
		key_already_exists(key.get('address'))
		import_key_remote(key.get('address'), sourceKey)
		data = { "address" : key.get('address') }
	except (json.JSONDecodeError, KeyFormatError):
		data = "key format nor recognized"
		status = 400
	except (KeyExistsError):
		data = "trying to import an existing key"
		status = 400
	
	user.add_key(key.get('address'), local=False)
	return {
		"data": data,
		"status": status
	}

def export_key(user, address, delete=False):

	keyDirectory = environ.get('KEYS_DIRECTORY')
	for keyFile in listdir(keyDirectory):
		if address in keyFile:
			with open(path.join(keyDirectory, keyFile), 'r') as f:
				data = json.load(f)
				if delete is True:
					remove(f.name)
					user.remove_key(address, local=False)
				return {
					"data": data,
					"status": 200
				}

	return {
		"data": "Key does not exists",
		"status": 400
	}
