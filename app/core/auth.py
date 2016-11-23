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
def login(creditentials):

	user = None

	def auth_user(creditentials):
		if creditentials:
			creditentials = str(b64decode(creditentials), 'utf-8').split(':')
			if len(creditentials) == 2:
				name, passw = creditentials[0], encode_hex(scrypt.hash(creditentials[1], "du gros sel s'il vous plait")).decode('utf-8')
				if (name is not None) and (passw is not None):
					user = users.find_one({"name": name, "password": passw}, users.user_info)
					return user
		return None

	if request.headers.get('authentification') is not None and request.headers.get('authentification') in session:
		return {
			"data": "already logged in",
			"status": 403
		}

	user = auth_user(creditentials.get('id'))

	if user is not None:
		token = str(jwt.encode({"name": user['name'], "timestamp": time.strftime("%a%d%b%Y%H%M%S")}, secret_key, algorithm='HS256'), 'utf-8')
		session[token] = user
		return {"data": {
					"token": token,
					"user": deserialize_user(user)
				},
				"status": 200}

	else:
		return {"data": "User does not exists of false password",
				"status": 401}

# remove token from session
def logout(user):
	token = request.headers.get('authentification')
	del session[token]
	return {"success": True}

def sign_up(newUser):

	def wrong_signup_request(newUser):
		required_fields = ["name", "password", "email"]
		for field in required_fields:
			if newUser.get(field) is None:
				return {"status": 403,
						"error": "missing required field"}
		return None

	def user_exists(newUser):
		if users.find({"email": newUser.get('email')}).count() > 0:
			return {"data": "user already exists",
					"status": 403}
		return False

	failure = wrong_signup_request(newUser) or user_exists(newUser)
	if failure:
		return failure

	unencryptedPassword = newUser.get('password')
	newUser["password"] = encode_hex(scrypt.hash(newUser.get('password'), "du gros sel s'il vous plait")).decode('utf-8')
	
	newKey = keys.gen_base_key() if newUser.get('eth') else None

	newUser["eth"] = {
		"mainKey": newKey,
		"keys": {newKey: {"local": False, "balance": 0, "address": newKey}} if newKey else [],
	}

	users.insert_one(newUser)
	newUser["_id"] = str(newUser["_id"])
	
	return login({"id": b64encode(bytearray(newUser.get('name'), 'utf-8') + b':' + bytearray(unencryptedPassword, 'utf-8'))})

def check_token_validity(token):
	return {"data": {"user": session.get(token)},
			"status": 200}

def delete_user(user):
	# _id = user.get("id")
	# users.remove({"id": _id})
	pass
