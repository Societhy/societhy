from mongokat import Collection, Document
from .clients import client

class FundraiseDocument(Document):
	pass

class FundraiseCollection(Collection):
	pass

fundraises = FundraiseCollection(collection=client.main.fundraises)