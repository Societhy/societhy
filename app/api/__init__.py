from functools import wraps
import jwt
from flask import session, request, Response
from core import secret_key

from models import users, UserDocument
from models.clients import client as mongo_client
from uuid import uuid4
from datetime import datetime, timedelta

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from pymongo import MongoClient


def ensure_fields(fields, request_data):
	for field in fields:
		if isinstance(field, dict):
			k = list(field.keys())[0]
			return ensure_fields(field.get(k), request_data.get(k))
		else:
			if field not in request_data:
				return False
	return True
	
# decorator that checks if a user is identified
def requires_auth(f):
	@wraps(f)
	def wrapped_function(*args, **kwargs):
		token = request.headers.get('authentification')
		if token is not None and token in session:
			try:
				token = token.replace('|', '.')
				jwt.decode(token, secret_key)
			except jwt.ExpiredSignatureError:
				return Response({"error": "signature expired"}, 401)
			except jwt.exceptions.DecodeError:
				return Response({"error": "Login required"}, 401)
			token = token.replace('.', '|')
			user = UserDocument(session.get(token), session=token)
			if session.get(token).get('needs_reloading') is True:
				user.reload()
				session[token]["needs_reloading"] = False
		else:
			return Response({"error": "unauthorized"}, 401)

		if request.json and request.json.get('socketid') != None:
			user['socketid'] = request.json.get('socketid')
		kwargs['user'] = user
		session[token] = user
		return f(*args, **kwargs)
	return wrapped_function

# decorator that checks if a user is identified
def populate_user(f):
	@wraps(f)
	def wrapped_function(*args, **kwargs):
		token = request.headers.get('authentification')
		if token is not None and token in session:
			try:
				token = token.replace('|', '.')
				jwt.decode(token, secret_key)
			except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
				kwargs['user'] = None
				return f(*args, **kwargs)
			token = token.replace('.', '|')
			user = UserDocument(session.get(token))
			if session.get(token).get('needs_reloading') is True:
				user.reload()
				session[token]["needs_reloading"] = False
		else:
			user = None

		kwargs['user'] = user
		return f(*args, **kwargs)
	return wrapped_function

class MongoSession(CallbackDict, SessionMixin):
	def __init__(self, initial=None, sid=None):
		CallbackDict.__init__(self, initial)
		self.sid = sid
		self.modified = False


class MongoSessionInterface(SessionInterface):
	def __init__(self, collection='sessions'):
		client = mongo_client;
		self.store = client['main'][collection]

	def open_session(self, app, request):
		sid = request.cookies.get(app.session_cookie_name)
		if sid:
			stored_session = self.store.find_one({'sid': sid})
			if stored_session:
				if stored_session.get('expiration') > datetime.utcnow():
					return MongoSession(initial=stored_session['data'],
										sid=stored_session['sid'])
		sid = str(uuid4())
		return MongoSession(sid=sid)

	def save_session(self, app, session, response):
		domain = self.get_cookie_domain(app)
		if not session:
			response.delete_cookie(app.session_cookie_name, domain=domain)
			return
		if self.get_expiration_time(app, session):
			expiration = self.get_expiration_time(app, session)
		else:
			expiration = datetime.utcnow() + timedelta(hours=1)
		self.store.update({'sid': session.sid},
						  {'sid': session.sid,
						   'data': session,
						   'expiration': expiration}, True, check_keys=False)
		response.set_cookie(app.session_cookie_name, session.sid,
							expires=self.get_expiration_time(app, session),
							httponly=False, domain=domain)
