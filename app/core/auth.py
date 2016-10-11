import time
import jwt
from base64 import b64decode, b64encode

from flask import session, request, Response
# from models import users

from . import secret_key

# users_table = {user.get('name'): user.get('id') for user in users.find()}
# users_table = dict()

users_table = {"simon": None}
users = {"simon": {
			"id": "1",
			"name": "simon",
			"password": "bite"
			}
		}

# users = dict()

# generates token for session
def login(creditentials):

	user = None

	def auth_user(creditentials):
		
		if creditentials:
			creditentials = str(b64decode(creditentials), 'utf-8').split(':')
			if len(creditentials) == 2:
				name, passw = creditentials[0], creditentials[1]
				if (name is not None) and (passw is not None) and (name in users_table):
					# user = users.find_by_id(users_table.get(name))
					user = users.get(name)
					if passw == user.get('password'):
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
	required_fields = ["name", "password"]
	for field in required_fields:
		if newUser.get(field) is None:
			return {"status": 403,
					"error": "missing required field"}


	print(newUser.get('name'), "--------------", users_table.keys())
	if newUser.get('name') in users_table:
		return {"data": "user already exists",
				"status": 403}

	# ret = users.insert_one(newUser)
	# users_table[newUser.get('name')] = ret.inserted_id
	users_table[newUser.get('name')] = '1'
	users[newUser.get('name')] = newUser
	return login({"id": b64encode(bytearray(newUser.get('name'), 'utf-8') + b':' + bytearray(newUser.get('password'), 'utf-8'))})

def check_token_validity(token):
	return {"data": {"user": session.get(token)},
			"status": 200}

def delete_user(user):
	_id = user.get("id")
	users.remove({"id": _id})
