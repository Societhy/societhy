from mongokat import Collection, Document
from .clients import client

categoryList = ('newMember', 'memberLeave', 'newProposition', 'newDonation', 'newSpending', 'newMessage', 'newFriendAdd')
senderList = ('organization', 'project', 'user')


class NotificationDocument(Document):
	def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None):
		super().__init__(doc=doc, mongokat_collection=notifications, fetched_fields=fetched_fields, gen_skel=gen_skel)

	def getSender(self):
		if self['sender']['senderType'] == 'organization':
			return organizations.find_one({"_id": self['sender']['senderId']})
		elif self['sender']['senderType'] == 'project':
			return projects.find_one({"_id": self['sender']['senderId']})
		elif self['sender']['senderType'] == 'user':
			return users.find_one({"_id": self['sender']['senderId']})

	def getSubject(self):
		return users.find_one({"_id": self["subjectId"]})


class NotificationCollection(Collection):
	document_class = NotificationDocument


notifications = NotificationCollection(collection=client.main.notification)
