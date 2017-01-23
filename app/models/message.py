from bson.objectid import ObjectId

from mongokat import Collection, Document
from .clients import client

class MessageDocument(Document):

	def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None):
		super().__init__(doc, messages, fetched_fields, gen_skel)

class MessageCollection(Collection):
	message_info = [
        "data",
        "date",
		"send_address",
        "recip_address",
        "avatar",
        "files"
	]

	document_class = MessageDocument

messages = MessageCollection(collection=client.main.messages)
