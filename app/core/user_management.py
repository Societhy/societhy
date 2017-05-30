"""
This module is used to handle request relative to the user.
Each function correspond to a route.
"""
import time
import jwt
import scrypt
import collections
from base64 import b64decode, b64encode

from bson.objectid import ObjectId
from rlp.utils import encode_hex
from flask import session, request, Response, jsonify


from models.notification import notifications
from models import users, UserDocument, organizations
from models.notification import notifications
from models import errors

from core import keys, base_orga
from . import secret_key


def update(user, newData):
	"""
	user : model that represent the user
	newData : object that reprensents the updated values.

	This function is used to update some fields of the user profile.

	- The field are updated thanks to the recurse_update() function.
	- The modifications are saved thanks to the save_partial() function of the model.
	- Fields are populate thanks to the generatePersonalDataFromSocial() and the data who come from a social provider.
	- OK-> 200
	"""
	def recurse_update(user, newData):
		"""
		This recursive function will iterate over the items in the new data.
		"""
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
	"""
	Legacy function.
	Dedicated to be deleted in the next refactoring.
	"""
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
	"""
	user : model that represent the user
	data : data provided by the request.

	This function is used to add a contact to a user's contact list.

	- The added users is searched in the database.
	- If he is found, he is added to the user contact list.
	- OK-> 200, error->400
	"""
	if users.find_one({'_id': ObjectId(data['contact']['id'])}) is None:
		return {'data': 'User doesn\' exists.',
                        'status': 401}
		users.update({"_id": ObjectId(data["_id"])}, {"$addToSet": {"contact_list": data["contact"]}})
		user = users.find_one({"_id": ObjectId(data["_id"])})
		return {"data": user,
        		"status": 200}

def delFromContact(user, data):
	"""
	user : model that represent the user
	data : data provided by the request.

	This function is used to delete a contact from a user's contact list.
	
	- An update is perform in the database.	
	- OK-> 200, error->400
	"""
	users.update({"_id": ObjectId(data["_id"])}, {"$pull": {"contact_list": {"id": data["contact"]["id"]}}})
	user = users.find_one({"_id": ObjectId(data["_id"])})
	return {"data": user,
        	"status": 200}

def isInContactList(userId, contactId):
	"""
	user : model that represent the user
	contactId : the ID the user is looking to

	This function is used to check if a user is in an other user's contact list.
	- An search is perform in the database.	
	- OK-> 200, error->400
	"""
	if users.find_one({'_id': ObjectId(userId), 'contact_list.id': contactId}) != None:
		return True
	return False

def findUser(data):
	"""
	data : the data provided.

	This function is used to get a user model document from a user id.
	- If the '_id' field is not provided, an error is returned.
	- The user in found in the database from his id.
	- The user is sent
	- OK-> 200, error->400
	"""
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

def getUserNotif(data):
	ret = list(notifications.find({"userId" : ObjectId(data.get("_id"))}, {"date" : 0, "_id" : 0}))
	return {"data": {"notifications": ret}, "status": 200}

def acceptInvitation(user, data):
	orga = organizations.find_one({"_id":ObjectId(data["orga_id"])})
	if str(user["_id"]) in orga["invited_users"]:
		item = orga["invited_users"][str(user["_id"])]
		print(user)
		ret = base_orga.joinOrga(user, data["password"], str(orga["_id"]), item["tag"])
		if (ret["status"] == 200):
			del orga["invited_users"][str(user["_id"])]
			orga.save()
			for item in user["pending_invitation"]:
				if item["id"] == str(orga["_id"]):
					user["pending_invitation"].remove(item)
			user.save()
			return({"data":"invitation accepted", "status":200})
		else:
			return ret
	else:
		return ({"data":"User not invited", "status":400})
