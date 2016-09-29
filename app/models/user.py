from mongokat import Collection, Document
from .db import client

class UserDocument(Document):
	pass

class UserCollection(Collection):
	pass

users = UserCollection(collection=client.main.users)
