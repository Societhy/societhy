import time
import ethjsonrpc
from base64 import b64decode, b64encode

from flask import session, request, Response
from models import users

def gen_linked_key(user):
	print(user)
	return {
		"data": "OK",
		"status": 200
	}

def key_was_generated(user, address):
	print(user, address)
	return {
		"data": "OK",
		"status": 200
	}

def import_new_key(user, key):
	print(key)
	return {
		"data": "OK",
		"status": 200
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
