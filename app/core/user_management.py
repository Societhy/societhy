import time
import jwt
import scrypt
from base64 import b64decode, b64encode

from flask import session, request, Response
from models import users, UserDocument

from core import keys
from core.utils import deserialize_user

from . import secret_key

from rlp.utils import encode_hex
# generates token for session

def update(user):


	def user_exists(user):
		if users.find({"email": user.get('email')}).count() < 0:
			return {"data": "user does not exists",
					"status": 403}
		return False

	failure = user_exists(user)
	if failure:
		return failure

	return ({"status":"ok"})

	# unencryptedPassword = newUser.get('password')
	# newUser["password"] = encode_hex(scrypt.hash(newUser.get('password'), "du gros sel s'il vous plait")).decode('utf-8')
	
	# newKey = keys.gen_key() if newUser.get('eth') else None
	# newUser["eth"] = {
	# 	"mainKey": newKey,
	# 	"keys": [newKey] if newKey else [],
	# }

	# users.insert_one(newUser)
	# newUser["_id"] = str(newUser["_id"])
	
	# return login({"id": b64encode(bytearray(newUser.get('name'), 'utf-8') + b':' + bytearray(unencryptedPassword, 'utf-8'))})
