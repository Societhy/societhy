from mongokat import Collection, Document
from .clients import client
from models.organization import organizations, OrgaDocument as organization
from models.project import projects,  ProjectDocument as project

categoryList = ('newMember', 'memberLeave', 'newProposition', 'newDonation', 'newSpending', 'newMessage', 'newFriendAdd')
senderList = ('organization', 'project', 'user')

class NotificationDocument(Document):
    def __init__(self,
    			 doc=None,
    			 mongokat_collection=None,
    			 fetched_fields=None,
    			 gen_skel=None,
    			 sender=None,
    			 senderType=None,
    			 category=None,
    			 description=None):
		super().__init__(doc=doc, mongokat_collection=organizations, fetched_fields=fetched_fields, gen_skel=gen_skel)
			self[sender] = senderType
			self[senderId] = sender["_id"]
			self[category] = category
			self[description] = description


			def getSender(self):
				pass

			def getSubject(self):
				pass

class NotificationCollection(Collection):
	document_class = NotificationDocument

notifications = NotificationCollection(collection=client.main.notifications)
