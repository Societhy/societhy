from mongokat import Collection, Document
from .clients import client

from bson.objectid import ObjectId
from bson import json_util
import json
from datetime import datetime

import models.organization
from models.user import users, UserDocument as user
from models.project import projects,  ProjectDocument as project
from models.clients import app
from flask_socketio import SocketIO, send, emit

class NotificationDocument(Document):

	def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None, session=None):
		super().__init__(doc=doc, mongokat_collection=notifications, fetched_fields=fetched_fields, gen_skel=gen_skel)
		self["seen"] = False

	def save(self, force=False, uuid=False, **kwargs):
		super().save(force=force, uuid=uuid, **kwargs)
		imp = __import__('core.chat', globals(), locals(), ['Clients'], 0)
		Clients = imp.Clients
		if self["subject"]["type"] == "user":
			if str(self["subject"]['id']) in Clients:
				with app.app_context():
					emit("update_notif", "copy me ?",  namespace='/', room=Clients[str(self["subject"]['id'])].sessionId)


	def pushNotif(data):
		print(data["subject"]["type"])
		notifications.insert({"subject" : { "id" : data["subject"]["id"], "type": data["subject"]["type"]},
                                      	"sender" : { "id" : data["sender"]["id"], "type": data["sender"]["type"]},
                                      	"category": data["category"],
                                      	"createdAt": datetime.now(),
                                      	"date": datetime.now().strftime("%b %d, %Y %I:%M %p"),
										"seen": False
                })


	def push(self, data):
		self["user"] = {"id":None}
		self["user"]["id"] = data["userId"]
		self["category"] = data["category"]
		self["sender"] = {"id":None, "name":None, "type":None}
		self["sender"]["id"] = data["sender"]["id"]
		self["sender"]["name"] = data["sender"]["name"]
		self["sender"]["type"] = data["sender"]["type"]
		self["date"] = datetime.now().strftime("%b %d, %Y %I:%M %p")
		self["createdAt"] = datetime.now()
		self["seen"] = False
		if data["subject"]["id"]:
			self["subject"] = {"id":None,  "type":None}
			self["subject"]["id"] = data["subject"]["id"]
			self["subject"]["type"] = data["subject"]["type"]
		print(self)
		self.save()


                
	def getSender(self):
		if self['sender']['senderType'] == 'organization':
			return organizations.find_one({"_id": self['sender']['senderId']})
		elif self['sender']['senderType'] == 'project':
			return projects.find_one({"_id": self['sender']['senderId']})
		elif self['sender']['senderType'] == 'user':
			return users.find_one({"_id": self['sender']['senderId']})
		return None

	def getName(data):
		name = None
		if data['type'] == 'orga':
			name = models.organization.organizations.find_one({"_id" : data['id']}, {"name": 1})
		elif data['type'] == 'user':
			name = users.find_one({"_id" : data['id']}, {"name": 1})
		if name == None:
			return "Unknown"
		return  name['name']
                
	def getHisto(_id, date):
		data = notifications.find({
                        "$and" : [
                                {"$or" : [
                                        {"sender.type" : "orga", "sender.id" : ObjectId(_id)},
                                        {"subject.type" : "orga", "subject.id" : ObjectId(_id)}
                                ]},
                                { "createdAt" : {
                                        "$gte" : datetime.strptime(date['begin'], "%b %d, %Y %I:%M %p"),
                                        "$lt" : datetime.strptime(date['end'], "%b %d, %Y %I:%M %p")
                                }}
                        ]},
                        {"_id": 0, "createdAt": 0})
		res = {}
		i = 0
		if data.count() != 0:
			for record in data:
				name = ""
				res[i] = record
				#res[i]['sender']['name'] = NotificationDocument.getName(record['sender'])
				#res[i]['subject']['name'] = NotificationDocument.getName(record['subject'])
				if record["category"] == "orgaCreate":
					res[0]["first"] = record["date"] 
				i = i + 1
			return res
		return []

	def getSubject(self):
		return users.find_one({"_id": self["subjectId"]})


class NotificationCollection(Collection):
	document_class = NotificationDocument

notifications = NotificationCollection(collection=client.main.notifications)
