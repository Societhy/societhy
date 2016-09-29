from mongokat import Collection, Document
from .db import client

class ContractDocument(Document):
	pass

class ContractCollection(Collection):
	pass

contracts = ContractCollection(collection=client.main.contracts)