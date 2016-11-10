import time
import jwt
import hashlib
from base64 import b64decode, b64encode

from flask import session, request, Response
from models import users
from core import eth

from . import secret_key

# generates token for session
def login(creditentials):

	user = None

	def auth_user(creditentials):

		if creditentials:
			creditentials = str(b64decode(creditentials), 'utf-8').split(':')
			if len(creditentials) == 2:
				name, passw = creditentials[0], hashlib.md5(creditentials[1].encode()).hexdigest()
				if (name is not None) and (passw is not None):
					user = users.find({"name": name, "password": passw})
					user = user[0] if user.count() >= 1 else None
					if user:
						user.update({"_id": str(user.get('_id'))})
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
					"user": user
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
	newUser["password"] = hashlib.md5(newUser.get('password').encode()).hexdigest()
	
	newKey = eth.gen_key() if newUser.get('eth') else None
	newUser["eth"] = {
		"mainKey": newKey,
		"keys": [newKey] if newKey else [],
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
