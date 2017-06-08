from mongokat import Collection, Document
from .clients import client

from bson.objectid import ObjectId
from bson import json_util
import json
from datetime import datetime

import models.organization
from models.user import users, UserDocument as user
from models.project import projects,  ProjectDocument as project

class TransactionDocument(Document):

	def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None, session=None):
		super().__init__(doc=doc, mongokat_collection=transactions, fetched_fields=fetched_fields, gen_skel=gen_skel)
		self["seen"] = False
                
class TransactionCollection(Collection):
	document_class = TransactionDocument

transactions = TransactionCollection(collection=client.main.transactions)
