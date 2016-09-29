from mongokat import Collection, Document
from .db import client

class FileDocument(Document):
	pass

class FileCollection(Collection):
	pass

files = FileCollection(collection=client.main.files)