"""
This module is used to implement Notification functionalities.
There is 3 classes who will modelise the differents kind of notifications, and a few tool functions.
"""
from flask import current_app
from flask_mail import Message

from bson.json_util import dumps

from datetime import datetime

from models.notification import notifications, NotificationDocument as Notification
from models.clients import mail

# Exemple for test #notifyToOne(organizations.find_one({"_id": ObjectId("58823a62fa25f07ac36d4b71")}), users.find_one({"_id" : ObjectId("5876417fcba72b00a03cf9f4")}), 'newSpending')

categoryList = ('newMember', 'memberLeave', 'newProposition', 'newDonation', 'newSpending', 'newMessage', 'newFriendAdd', 'orgaCreated', 'projectCreated', 'newInviteJoinOrga')
descriptionList = (' is the new member of ', ' leave ', 'did a new proposition', ' give to ', ' spend ', ' send you a message', ' send you a friend request', " created ", ' created ', ' invited you to join the organisation')
senderList = ('organization', 'project', 'user')


def createDescription(category):
	"""
	Depending of the category, this function will fill the description.
	"""
	i = 0
	for tmp in categoryList:
		if tmp in category:
			print(tmp)
			print(descriptionList[i])
			description = descriptionList[i]
			return description
		i = i + 1
	return None


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
		description = createDescription(category)
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
	description = createDescription(category)
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



def getUserUnreadNotification(user):
	unread_notifs = list(notifications.find({"subject.id":user.get("_id"), "seen":False }))
	for notif in unread_notifs:
		notif["description"] = createDescription(notif["category"])
	return {
		"data" : dumps(unread_notifs),
		"status" : 200
	}