from functools import wraps
import jwt
from flask import session, request, Response
from core import secret_key

from models import users, UserDocument

# decorator that checks if a user is identified
def requires_auth(f):
	@wraps(f)
	def wrapped_function(*args, **kwargs):
		token = request.headers.get('authentification')
		if token is not None and token in session:
			try:
				jwt.decode(token, secret_key)
			except jwt.ExpiredSignatureError:
				return Response({"error": "signature expired"}, 401)

			user = UserDocument(session.get(token))
			user.update()
		else:
			return Response({"error": "unauthorized"}, 401)

		kwargs['user'] = user
		session[token] = user
		return f(*args, **kwargs)
	return wrapped_function
