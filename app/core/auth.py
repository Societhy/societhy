import time
import jwt
import scrypt
from base64 import b64decode, b64encode
from bson.objectid import ObjectId

from flask import session, request, Response
from models import users, UserDocument

from core import keys
from core.utils import deserializeUser

from . import secret_key, SALT_LOGIN_PASSWORD

from rlp.utils import encode_hex
# generates token for session

def login(credentials):

	user = None

	def authUser(credentials):
		if credentials:
			credentials = str(b64decode(credentials), 'utf-8').split(':')
			if len(credentials) == 2:
				name, passw = credentials[0], encode_hex(scrypt.hash(credentials[1], SALT_LOGIN_PASSWORD)).decode('utf-8')
				if (name is not None) and (passw is not None):
					user = users.find_one({"name": name, "password": passw}, users.user_info)
					return user
		return None

	def authUserSocial(credentials):
		return users.find_one({("social.%s.id" % credentials["provider"]) : credentials["socialId"]})

	if request.headers.get('authentification') is not None and request.headers.get('authentification') in session:
		return {
			"data": "already logged in",
			"status": 403
		}

	if "socialId" not in credentials:
		user = authUser(credentials.get('id'))
	else:
		user = authUserSocial(credentials)

	if user is not None:
		token = str(jwt.encode({"_id": str(user.get("_id")), "timestamp": time.strftime("%a%d%b%Y%H%M%S")}, secret_key, algorithm='HS256'), 'utf-8')
		user["socketid"] = credentials.get('socketid')
		session[token] = user
		return {"data": {
					"token": token,
					"user": deserializeUser(user)
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

def signUp(newUser):

	def wrongSignupRequest(newUser):
		required_fields = ["name", "password", "email"]
		for field in required_fields:
			if newUser.get(field) is None:
				return {"status": 403,
						"error": "missing required field"}
		return None

	def userExists(newUser):
		if users.find({"email": newUser.get('email')}).count() > 0:
			return {"data": "user already exists",
					"status": 403}
		return False

	def socialUserExists(newUser):
		social_provider = list(newUser.get('social').keys())[0]
		social_id = newUser.get('social').get(social_provider).get('id')
		social_email = newUser.get('social').get(social_provider).get('email')
		if users.find({'$or': [{("social.%s.id" % social_provider) : newUser["social"][social_provider]["id"]},
								{"email": social_email}]}).count() > 0:
			return None
		else:
			return {"social_id": social_id, "social_provider": social_provider}

	if 'social' not in newUser:
		failure = wrongSignupRequest(newUser) or userExists(newUser)
		if failure is True:
			return failure

		unencryptedPassword = newUser.get('password')
		newUser["password"] = encode_hex(scrypt.hash(newUser.get('password'), SALT_LOGIN_PASSWORD)).decode('utf-8')
		user = UserDocument(newUser, gen_skel=True)
		user.save()
		if user.get('eth'):
			del user["eth"]
			user.populateKey()
		else:
			user["eth"] = {}
			user.save_partial()

		return login({"id": b64encode(bytearray(newUser.get('name'), 'utf-8') + b':' + bytearray(unencryptedPassword, 'utf-8')),
					"socketid": newUser.get('socketid')})

	else:
		social_infos = socialUserExists(newUser)
		if social_infos is None:
			return {"data": "user already exists", "status": 403}

		newUser["password"] = encode_hex(scrypt.hash("password", SALT_LOGIN_PASSWORD)).decode('utf-8')
		user = UserDocument(newUser, gen_skel=True)
		user.save()
		if user.get('eth'):
			del user["eth"]
			user.populateKey()
		else:
			user["eth"] = {}
			user.save_partial()

		user.generatePersonalDataFromSocial()
		return login({"socialId": social_infos.get('social_id'),
						"provider": social_infos.get('social_provider'),
						"socketid": newUser.get('socketid')})


def setSocketId(socketid, user):
	if user:
		user['socketid'] = socketid
		token = request.headers.get('authentification')
		session[token] = user
	return {"data": user,
			"status": 200}

def checkTokenValidity(token, user):
	return {"data": {"user": session.get(token)},
			"status": 200}

def deleteUser(user):
	logout(user)
	user.delete()
	return {"data": "User deleted successfully",
			"status": 200}
