import time
import jwt
from functools import wraps
from base64 import b64decode

from flask import session, request, Response
from models import users

# decorator that checks if a user is identified

# users_table = {user.get("username"): user.get("password") for user in users.find()}
users_table = {"simon": "bite"}

def requires_auth(f):
	@wraps(f)
	def function(*args, **kwargs):
		from app import secret_key
		token = request.headers.get('authentification')
		if token is not None and token in session:
			try:
				jwt.decode(token, secret_key)
			except jwt.ExpiredSignatureError:
				return Response({"error": "signature expired"}, 401)
		else:
			return Response({"error": "unauthorized"}, 401)

		return f(*args, **kwargs)
	return function

# generates token for session
def login(creditentials):

	from app import secret_key
	user = None

	def auth_user(creditentials):
		nonlocal user
		creditentials = str(b64decode(creditentials), 'utf-8').split(':')
		if len(creditentials) == 2:
			user = {
				"name": creditentials[0],
				"password": creditentials[1]
			 }
			if user["name"] is not None \
				and user["name"] in users_table \
				and users_table.get(user["name"]) == user["password"]:
				return True
			else:
				return False

	if request.headers.get('authentification') is not None and request.headers.get('authentification') in session:
		return {
			"error": "already logged in",
			"status": 403
		}
	if creditentials.get('id') is not None and auth_user(creditentials['id']):
		token = str(jwt.encode({"name": user["name"], "timestamp": time.strftime("%a%d%b%Y%H%M%S")}, secret_key, algorithm='HS256'), 'utf-8')
		session[token] = True
		return {"data": {"token": token},
				"status": 200}
	else:
		return {"error": True,
				"status": 401}

# remove token from session
def logout():
	token = request.headers.get('authentification')
	del session[token]
	return {"success": True}
	
def sign_up(newUser):
	required_fields = ["name", "email", "password"]
	if len([field for field in required_fields if field in newUser.keys()]) < len(required_fields):
		return {"success": False,
				"reason": "missing required field"}

	if newUser.get('name') is None or users.find_one({'name': name}) is not None:
		return {"success": False}
	return {"success": True}

def delete_user(user):
	user = users.find_one({"name": user})
	if user is not None:
		users.remove(user)
