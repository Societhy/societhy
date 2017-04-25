from flask_mail import Message, Mail
from flask_socketio import SocketIO, send, emit
from models.clients import socketio
from models.user import users, UserDocument as User
from models.project import projects, ProjectDocument as Project
from models.organization import organizations, OrgaDocument as Orga
from models.notification import notifications, NotificationDocument as Notification
#from core.chat import notify
import datetime

# Exemple for test #notifyToOne(organizations.find_one({"_id": ObjectId("58823a62fa25f07ac36d4b71")}), users.find_one({"_id" : ObjectId("5876417fcba72b00a03cf9f4")}), 'newSpending')

class Notification():
	categoryList = ('newMember', 'memberLeave', 'newProposition', 'newDonation', 'newSpending', 'newMessage', 'newFriendAdd')
	descriptionList = (' is the new member of ', ' leave ', 'did a new proposition', ' give to ', ' spend ', ' send you a message', ' send you a friend request')
	senderList = ('organization', 'project', 'user')

	def createDescription(self, category):
		i = 0
		for tmp in self.categoryList:
			if tmp in category:
				self.description = self.descriptionList[i]
				return True
			i = i + 1
		return False

class NotificationPush(Notification):
	def sendNotif(self, sender, senderType, category, subject, user):
		print("notif push")
		if self.createDescription(category) == False:
			return "unsent"
		print("insert")
		if subject:
			subjectType = findType(subject)
			notifications.insert({"userId" : user.get("_id"), "sender": { "senderId": sender.get("_id"), "senderName" : sender.get("name"), "senderType": senderType}, "subject" : {"subjectId" : subject.get("_id"), "subjectType" : subjectType}, "category":category, "date": datetime.datetime.now(), "description":self.description})
		else:
			notifications.insert({"userId" : user.get("_id"), "sender": { "senderId": sender.get("_id"), "senderType": senderType}, "category":category, "date": datetime.datetime.now(), "description":self.description})

class NotificationEmail(Notification):
	def sendNotif(self, sender, senderType, category, subject, user):
		print("notif email")
		if self.createDescription(category) == False:
			return "unsent"
		msg = Message(category, sender = 'societhycompany@gmail.com', recipients = [user.get("email")])
		if subject:
			msg.body = subject.get("name") + self.description + sender.get("name")
		else:
			msg.body = sender.get("name") + self.description
		print("sent")
		global mail
		_mail.send(msg)
		return "sent"

def notifyToOne(sender, user, category, subject=None):
	senderType = findType(sender)
	print("OEEE")
	if senderType == None:
		return
	#	return
	#print(user.get("notification_accept"))
	#if user.get("notification_accept") == 0:
	#	return
	#elif user.get("notification_accept") == 1 or user.get("notification_accept") == 3:
	#push = NotificationPush()
	#notify(push, sender, senderType, category, subject, user)
	#if user.get("notification_accept") == 2 or user.get("notification_accept") == 3:
	print("weeeeeeeee")
	email = NotificationEmail()
	print("louheee")
	email.sendNotif(sender, senderType, category, subject, user)

def findType(doc):
	if isinstance(doc, User):
		return "user"
	elif isinstance(doc, Orga):
		return "organization"
	elif isinstance(doc, Project):
		return "project"
	return None