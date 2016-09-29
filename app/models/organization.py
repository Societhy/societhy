from mongokat import Collection, Document
from .db import client

class OrgaDocument(Document):
	pass

class OrgaCollection(Collection):
	pass

organizations = OrgaCollection(collection=client.main.organizations)