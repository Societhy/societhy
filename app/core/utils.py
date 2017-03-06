from copy import copy
from bson.objectid import ObjectId
import json

class UserJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def fromWei(value):
	return value / (10 ** 18)

def toWei(value):
	return int(value * (10 ** 18))

def serializeUser(user):
	serialized = copy(user)
	serialized.update({"_id": ObjectId(user.get('_id'))})
	return serialized

def deserializeUser(user):
	deserialized = copy(user)
	deserialized.update({"_id": str(user.get('_id'))})
	return deserialized

def normalizeAddress(address, hexa=False):
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