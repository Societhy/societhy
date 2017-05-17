"""
This module handle all the authentification process.
The two mains functions are login and register. They contains theirs owns userful functions.
"""

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
	"""
	credentials : data who come from the request.
	This function has as purpose to log in an exsting user.
	The login function first check if the account who tring to log is a social account (Facebook, ..) or a regular.
	The difference is that the social account does not have a password, the auth part is handled by a third party webservice who is OAuth compliant.
	The user is logged in the socketIO session.
	Then it will check if the account exists, and if he is already logged-in. If this is the case, and error will be sent with a 401/403 error code.
	Then, a session token will be generated, used for authentificate the further requests to the api.
	Finally, the full data about users will be returned to him, with a 200 status code.
	"""
	user = None

	def authUser(credentials):
		"""
		This function is for finding the user who attempt to log-in when he does have a regular account
		To check if a user exist, the password is salt according to the security specifications.
		After this, a db request is performed with the find_one method of the user model.
		Then, None or User variable is returned.
		"""
		if credentials:
			credentials = str(b64decode(credentials), 'utf-8').split(':')
			if len(credentials) == 2:
				name, passw = credentials[0], encode_hex(scrypt.hash(credentials[1], SALT_LOGIN_PASSWORD))
				if (name is not None) and (passw is not None):
					user = users.find_one({"name": name, "password": passw}, users.user_info)
					return user
		return None

	def authUserSocial(credentials):
		"""
		This function is for find the user who attempt to log-in when he does have a social account
		The same process of authUser if done here, but there is no need to sale/check the password, since all that part is done by the OAuth third party.
		As long as the user is logged with his social account, whe just have to find him in the database.
		"""
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
		token = token.replace('.', '|')
		setSocketId(credentials.get('socketid'), user)
		session[token] = user
		return {"data": {
					"token": token,
					"user": deserializeUser(user)
				},
				"status": 200}

	else:
		return {"data": "User does not exists of false password",
				"status": 401}

def logout(user):
	"""
	To log-out a user, whe juste have to delete his session token frome the actives ones.
	So when he will want to perform a request he will no be find and he will get a "not logged in" error.
	"""
	token = request.headers.get('authentification')
	del session[token]
	return {"success": True}

def signUp(newUser):
	"""
	newUser : the data provided by the request
	This function have as purpose to register to societhy an non-existing user.
	The first job is to check if this is a social connection with OAuth or a regular one.
	If this is a regular connection:
		- There is a verifcation the check if the request complies to the API specifications, and if the users does not exist.
		If this is the case, a 403 status code
		- The password is hashed and salted in order to get inserted in base
		- a new UserDocument is generated thanks to the data provided in the request.
		UserDocument represent the user data model, it is defined in the model folder.
		- The user is inserted in database thanks to the save() method of the user model.
		- The ethereum key is populated
		- The login object containing the user data is returned to the client with a 200 status code.
	If this is a social connections:
		- There is a verifcation the check if the request complies to the API specifications, and if the users does not exist.
		If this is the case, a 403 status code
		- a new UserDocument is generated thanks to the data provided in the request.
		- The user is inserted in database thanks to the save() method of the user model.
		- The generatePersonalDataFromSocial is used to generate user info in the database from the data provided by the social third party. 
		- The ethereum key is populated
		- The login object containing the user data is returned the the client with a 200 status code.
	"""
	def wrongSignupRequest(newUser):
		"""
		newuser : object extracted from the request data that describe the user who is trying to register.
		This function check if all the mandatory field of the signup process are filled.
		It return the error code if there is, none if all is OK.
		"""
		required_fields = ["name", "password", "email"]
		for field in required_fields:
			if newUser.get(field) is None:
				return {"status": 403,
						"error": "missing required field"}
		return None

	def userExists(newUser):
		"""
		newuser : object extracted from the request data that describe the user who is trying to register.
		This function check if the user is not already registered.
		It return the error code if there is, none if all is OK.
		"""
		if users.find({"email": newUser.get('email')}).count() > 0:
			return {"data": "user already exists",
					"status": 403}
		return False

	def socialUserExists(newUser):
		"""
		Same logic that userExists() but for the social log-in
		"""
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
		if failure:
			return failure

		unencryptedPassword = newUser.get('password')
		newUser["password"] = encode_hex(scrypt.hash(newUser.get('password'), SALT_LOGIN_PASSWORD))
		user = UserDocument(newUser, gen_skel=True)
		user.save()
		if user.get('eth'):
			del user["eth"]
			user.populateKey()
		else:
			user["eth"] = {"keys":{}}
			user.save_partial()

		return login({"id": b64encode(bytearray(newUser.get('name'), 'utf-8') + b':' + bytearray(unencryptedPassword, 'utf-8')),
					"socketid": newUser.get('socketid')})

	else:
		social_infos = socialUserExists(newUser)
		if social_infos is None:
			return {"data": "user already exists", "status": 403}

		newUser["password"] = encode_hex(scrypt.hash("password", SALT_LOGIN_PASSWORD))
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
	"""
	socketId: The id of the socket opened for the logged user.
	user: model document that modelise the user.
	The id is registered to the socketIO IDs list.
	"""
	if user:
		user['socketid'] = socketid
		user.save_partial()
		user.needsReloading()
		session.modified = True
	return {"data": user,
			"status": 200}

def checkTokenValidity(token, user):
	"""
	token: the user's session token
	user: model document that modelise the user.
	Return the user corresponding to a token
	"""
	return {"data": {"user": session.get(token)},
			"status": 200}

def deleteUser(user):
	"""
	user: model document that modelise the user.
	logout the user, then call the delete() method of the user model document.
	"""
	logout(user)
	user.delete()
	return {"data": "User deleted successfully",
			"status": 200}
