"""
In developpement.
"""
from mongokat import Collection, Document

from .clients import client


class FileDocument(Document):
	pass

class FileCollection(Collection):
	pass

files = FileCollection(collection=client.main.files)