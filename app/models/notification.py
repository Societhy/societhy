from datetime import datetime

import models.organization
import models.project
import models.user
from bson.objectid import ObjectId
from flask_mail import Message
from mongokat import Collection, Document

from .clients import client, mail

descriptionDict = {
	"NewMember":" is the new member of ",
	"MemberLeft": " leave ",
	"ProposalCreated": "did a new proposition",
	"DonationMade": " give to ",
	"newSpending": " spend ",
	"newMessage": " send you a message",
	"newFriendAdd": " send you a friend request",
	"orgaCreated": "invited you to join the organisation ",
	"ProjectCreated": "created a new project ",
	"newInviteJoinOrga": " invited you to join the orga",
	"OfferCreated": " created a new offer"
}

senderList = ('organization', 'project', 'user')

def sendNotifPush(sender, senderType, category, subject, user):
	"""
	Insert the notification in the database in order to be sent.
	"""
	imp = __import__('core.chat', globals(), locals(), ['Clients'], 0)
	Clients = imp.Clients
	if (user['_id'] in Clients):
		notif = {
				'description': push.createDescription(category),
				'subject_name': subject['name'],
				'sender_name': sender['name']
			}
		emit('send_message', notif, namespace='/', room=Clients[user['_id']].sessionId)
	else:
		notification = Notification()
		description = descriptionDict[category]
		if not description:
			return
		print("insert")
		if subject:
			subjectType = type(sender).__name__
			if not subjectType:
				return
			data = {"userId" : user.get("_id"), 
			"sender": { "id": sender.get("_id"), "name" : sender.get("name"), "type": senderType},
			"subject" : { "id" : subject.get("_id"), "type" : subjectType}, 
			"category":category, 
			"description":description}
			notification.push(data)
		else:
			data = {"userId" : user.get("_id"), 
			"sender": { "id": sender.get("_id"), "type": senderType}, 
			"category":category,
			"description":description}
			notification.push(data)

def sendNotifEmail(sender, senderType, category, subject, user):
	from app import app
	"""
	Insert the notification in the database in order to be sent.
	"""
	print("notif email")
	description = descriptionDict[category]
	if not description:
		return None
	msg = Message(category, sender = 'societhycompany@gmail.com', recipients = [user.get("email")])
	if subject:
		msg.body = subject.get("name") + description + sender.get("name")
	else:
		msg.body = sender.get("name") + description
	print("sent")
	with app.app_context():
		mail.send(msg)
	return msg

def notifyToOne(sender, user, category, subject=None):
	"""
	Used to send a notification depending of the type.
	"""
	senderType = type(sender).__name__
	print("OEEE")
	if not senderType:
		return
	#print(user.get("notification_accept"))
	#if user.get("notification_accept") == 0:
	#	return
	#elif user.get("notification_accept") == 1 or user.get("notification_accept") == 3:
	sendNotifPush(sender, senderType, category, subject, user)
	#if user.get("notification_accept") == 2 or user.get("notification_accept") == 3:
	sendNotifEmail(sender, senderType, category, subject, user)

class NotificationDocument(Document):

	def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None, session=None):
		super().__init__(doc=doc, mongokat_collection=notifications, fetched_fields=fetched_fields, gen_skel=gen_skel)
		self["seen"] = False

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
			return models.organization.organizations.find_one({"_id": self['sender']['senderId']})
		elif self['sender']['senderType'] == 'project':
			return models.project.projects.find_one({"_id": self['sender']['senderId']})
		elif self['sender']['senderType'] == 'user':
			return models.user.users.find_one({"_id": self['sender']['senderId']})
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
