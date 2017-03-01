import time
import jwt
import scrypt
import collections
from base64 import b64decode, b64encode
from bson.objectid import ObjectId
from flask import session, request, Response
from rlp.utils import encode_hex

from models import users, UserDocument
from models.notification import notifications
from models import errors

from core import keys
from . import secret_key


def update(user, newData):
	def recurse_update(user, newData):
		for key, value in newData.items():
			if isinstance(value, collections.Mapping):
				r = recurse_update(user.get(key, {}), value)
				user[key] = r
			else:
				user[key] = newData[key]
		return user

	user = recurse_update(user, newData)
	user.save_partial()
	user.generatePersonalDataFromSocial()
	return {"data": user,
		"status": 200}


def updateSingleUserField(user, newData):
	def fieldExist(data):
		if users.find({"_id": ObjectId(data["_id"])}).count() <= 0:
			return {"data": "Cannot find the user and with the corresponding data. Please logout, login and try again",
				"status": 401}
		return False

	error = fieldExist(newData)
	if error:
		return error

	user[newData["name"]] = newData["new"];
	user.save_partial()
	return {"data": user,
		"status": 200}

def addToContact(user, data):
    if users.find_one({'_id': ObjectId(data['contact']['id'])}) is None:
        return {'data': 'User doesn\' exists.',
            'status': 401}
    users.update({"_id": ObjectId(data["_id"])}, {"$addToSet": {"contact_list": data["contact"]}})
    user = users.find_one({"_id": ObjectId(data["_id"])})
    return {"data": user,
        "status": 200}

def delFromContact(user, data):
    users.update({"_id": ObjectId(data["_id"])}, {"$pull": {"contact_list": {"id": data["contact"]["id"]}}})
    user = users.find_one({"_id": ObjectId(data["_id"])})
    return {"data": user,
        "status": 200}

def isInContactList(userId, contactId):
    if users.find_one({'_id': ObjectId(userId), 'contact_list.id': contactId}) != None:
        return True
    return False

def findUser(data):
	if data.get('_id'):
		try:
			_id = ObjectId(data.get('_id'))
		except errors.InvalidId:
			return {"data": "Not a valid ObjectId, it must be a 12-byte input or a 24-character hex string", "status": 400}

		user = users.find_one({"_id": _id})
		return {"data": user,
			"status": 200}
	else:
		return {"data": "User's id is required to view its profile", "status":400}
