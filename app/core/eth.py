import time
import json
from base64 import b64decode, b64encode

from flask import session, request, Response

from models import users
from models.db import eth_cli

class KeyFormatError(Exception):
	pass

def gen_key():
	return "xx"

def gen_linked_key(user):

	print(user)
	# call ethjsonrpc to gen key
	return {
		"data": "OK",
		"status": 200
	}

def key_was_generated(user, address):
	print('---------------------', user, address)
	if user.get('addresses') is not None:
		user["addresses"].append({
			"address": address,
			"local": True
		 })
	else:
		user = [{
			"address": address,
			"local": True
		 }]
	users.update_one(user)
	return {
		"data": "OK",
		"status": 200
	}

def import_new_key(user, sourceKey):

	def isEthereumKey(keyFile):
		required_entries = set(["address", "crypto", "id", "version"])
		if not required_entries.issubset(set(keyFile.keys())):
			raise KeyFormatError

	status = 200
	sourceKey = sourceKey.read().decode('utf-8')

	try:
		key = json.loads(sourceKey)
		isEthereumKey(key)
		data = { "address" : key.get('address') }
	except (json.JSONDecodeError, KeyFormatError):
		data = "key format nor recognized"
		status = 400
	
	return {
		"data": data,
		"status": status
	}

def export_and_delete_key(user, address):
	print(address)
	return {
		"data": "OK",
		"status": 200
	}

def export_key(user, address):
	print(address)
	return {
		"data": "OK",
		"status": 200
	}
