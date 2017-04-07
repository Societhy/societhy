"""
This modules contains tools function that might me used by the models or the controllers.
"""
from copy import copy
from bson.objectid import ObjectId
import json

class UserJSONEncoder(json.JSONEncoder):
	"""
	Used to change ObjectId object in sring in order to be transmitted on a HTTP pipe.
	Otherwise, ObjectId can't be transmitted.
	"""
	def default(self, o):
	        if isinstance(o, ObjectId):
	            return str(o)
	        return json.JSONEncoder.default(self, o)

def fromWei(value):
	"""
	value : the value to compute.

	This function is used to divide the value with 10^18.
	User to get Wei from Ether (unit conversion)
	"""
	return value / (10 ** 18)

def toWei(value):
	"""
	value : the value to compute.

	This function is used to multiply the value with 10^18.
	User to get Ether from Wei (unit conversion)
	"""
	return int(value * (10 ** 18))

def serializeUser(user):
	"""
	Legacy function.
	Dedicated to be deleted in the next refactoring.
	"""
	serialized = copy(user)
	serialized.update({"_id": ObjectId(user.get('_id'))})
	return serialized

def deserializeUser(user):
	"""
	Legacy function.
	Dedicated to be deleted in the next refactoring.
	"""

	deserialized = copy(user)
	deserialized.update({"_id": str(user.get('_id'))})
	return deserialized

def normalizeAddress(address, hexa=False):
	"""
	address : the address.

	Used to re-syntax an Ethereum address.
	"""
	if len(address) > 40:
		address = address[len(address) - 40:]

	if hexa is True:
		return address if address.startswith("0x") else '0x' + address
	else:
		return address[2:] if address.startswith("0x") else address

def to32bytes(data): 
    data = data.replace('0x', '')
    padding_lenght = 64 - len(data)
    return '0x' + '0' * padding_lenght + data

def to20bytes(data):
	if len(data) > 40:
		data = data[-40:]
	return '0x' + data
