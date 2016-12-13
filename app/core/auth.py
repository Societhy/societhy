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

def login(credentials):

	user = None

	def auth_user(credentials):
		if credentials:
			credentials = str(b64decode(credentials), 'utf-8').split(':')
			if len(credentials) == 2:
				name, passw = credentials[0], encode_hex(scrypt.hash(credentials[1], "du gros sel s'il vous plait")).decode('utf-8')
				if (name is not None) and (passw is not None):
					user = users.find_one({"name": name, "password": passw}, users.user_info)
					return user
		return None

	def auth_user_social(credentials):
		print(credentials)
		if credentials["provider"] == "facebook":
			return users.find_one({"social.facebook.id" : credentials["socialId"]})
		if credentials["provider"] == "github":
			return users.find_one({"social.github.id" : credentials["socialId"]})
		if credentials["provider"] == "coinbase" :
			return users.find_one({"social.coinbase.id" : credentials["socialId"]})
		if credentials["provider"] == "linkedin":
			return users.find_one({"social.linkedin.id" : credentials["socialId"]})
		if credentials["provider"] == "twitter":
			return users.find_one({"social.twitter.id" : credentials["socialId"]})
		if credentials["provider"] == "google":
			return users.find_one({"social.google.id" : credentials["socialId"]})



	if request.headers.get('authentification') is not None and request.headers.get('authentification') in session:
		return {
			"data": "already logged in",
			"status": 403
		}

	if "socialId" not in credentials:
		print(credentials)
		user = auth_user(credentials.get('id'))
	else:
		user = auth_user_social(credentials)

	if user is not None:
		token = str(jwt.encode({"_id": str(user.get("_id")), "timestamp": time.strftime("%a%d%b%Y%H%M%S")}, secret_key, algorithm='HS256'), 'utf-8')
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

	def social_user_exists(newUser):
		if 'facebook' in newUser["social"]:
			if users.find({"social.facebook.id" : newUser["social"]["facebook"]["id"]}).count() > 0:
				return {"data": "user already exists", "status": 403}
		if 'github' in newUser["social"]:
			if users.find({"social.github.id" : newUser["social"]["github"]["id"]}).count() > 0:
				return {"data": "user already exists", "status": 403}
		if 'coinbase' in newUser["social"]:
			if users.find({"social.coinbase.id" : newUser["social"]["coinbase"]["id"]}).count() > 0:
				return {"data": "user already exists", "status": 403}
		if 'linkedin' in newUser["social"]:
			if users.find({"social.linkedin.id" : newUser["social"]["linkedin"]["id"]}).count() > 0:
				return {"data": "user already exists", "status": 403}
		if 'twitter' in newUser["social"]:
			if users.find({"social.twitter.id" : newUser["social"]["twitter"]["id"]}).count() > 0:
				return {"data": "user already exists", "status": 403}
		if 'google' in newUser["social"]:
			if users.find({"social.facebook.id" : newUser["social"]["google"]["id"]}).count() > 0:
				return {"data": "user already exists", "status": 403}


	if 'social' not in newUser:
		failure = wrong_signup_request(newUser) or user_exists(newUser)
		if failure:
			return failure

		unencryptedPassword = newUser.get('password')
		newUser["password"] = encode_hex(scrypt.hash(newUser.get('password'), "du gros sel s'il vous plait")).decode('utf-8')
				
		user = UserDocument(newUser, mongokat_collection=users)
		user.save()
		user.populate_key()
		return login({"id": b64encode(bytearray(newUser.get('name'), 'utf-8') + b':' + bytearray(unencryptedPassword, 'utf-8'))})

	else:
		failure = social_user_exists(newUser)
		if failure:
			return failure
		newUser = gen_key(newUser)
		user = UserDocument(newUser, mongokat_collection=users)
		user.save()
		user.populate_key()
		user.generatePersonalDataFromSocial()
		return {"data": newUser, "status": 200}




def check_token_validity(token):
	return {"data": {"user": session.get(token)},
			"status": 200}

def delete_user(user):
	# _id = user.get("id")
	# users.remove({"id": _id})
	pass
