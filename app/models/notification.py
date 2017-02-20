from mongokat import Collection, Document
from .clients import client

from bson.objectid import ObjectId
from bson import json_util
import json
import datetime

from models.organization import organizations, OrgaDocument as organization
from models.user import users, UserDocument as user
from models.project import projects,  ProjectDocument as project


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

	def getName(data):
		name = None
		if data['type'] == 'organization':
			name = organizations.find_one({"_id" : data['id']}, {"name": 1})
		elif data['type'] == 'user':
			name = users.find_one({"_id" : data['id']}, {"name": 1})
		if name == None:
			return "Unknown"
		return  name['name']

	def date_handler(obj):
		if hasattr(obj, 'isoformat'):
			return obj.isoformat()
		else:
			return obj
                
	def getHisto(_id, date):
#		notifications.insert({"subject" : { "id" : ObjectId("58823a62fa25f07ac36d4b71"), "type": "organization"},
#                                      "sender" : { "id" : ObjectId("587f0069082c0c0055c3c4d4"), "type": "user"},
#                                      "category": "newMember",
#                                      "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p"), "description": "new user"})
		
		data = notifications.find({
                                "$or" : [{"sender.type" : "organization", "sender.id" : ObjectId(_id)},{"subject.type" : "organization", "subject.id" : ObjectId(_id)}]}).sort("_id", -1)
		res = {}
		i = 0
		for record in data:
			name = ""
			res[i] = record
			res[i]['sender']['name'] = NotificationDocument.getName(record['sender'])
			res[i]['subject']['name'] = NotificationDocument.getName(record['subject'])
			res[i]["date"] = NotificationDocument.date_handler(res[i]["date"])
			i = i + 1
		return res

	def getSubject(self):
		return users.find_one({"_id": self["subjectId"]})


class NotificationCollection(Collection):
	document_class = NotificationDocument


notifications = NotificationCollection(collection=client.main.notification)
