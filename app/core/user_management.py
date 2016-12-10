import time
import jwt
import scrypt
from base64 import b64decode, b64encode

from flask import session, request, Response
from models import users, UserDocument

from bson.objectid import ObjectId

from core import keys
from core.utils import deserialize_user

from . import secret_key

from rlp.utils import encode_hex
# generates token for session

def update(user, newData):
	user.update(newData)
	print(newData)
	user.save_partial()
	return {"data": user,
		"status": 200}


def updateUserField(user, newData):
	def field_exist(data):
		if users.find({"_id": ObjectId(data["_id"]),
				data["name"]: data["old"]}).count() <= 0:
			return {"data": "Cannot find the user and with the corresponding data. Please logout, login and try again",
				"status": 401}
		return False

	error = field_exist(newData)
	if error:
		return error

	user[newData["name"]] = newData["new"];
	user.save_partial()
	return {"data": user,
		"status": 200}
