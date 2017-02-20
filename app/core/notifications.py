from app import *

from flask_mail import Message
from models.user import users, UserDocument as User
from models.project import projects, ProjectDocument as Project
from models.organization import organizations, OrgaDocument as Orga
from models.notification import notifications, NotificationDocument as Notification
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
			notifications.insert({"userId" : user.get("_id"), "sender": { "senderId": sender.get("_id"), "senderType": senderType}, "subject" : {"subjectId" : subject.get("_id"), "subjectType" : subjectType}, "category":category, "date": datetime.datetime.now(), "description":self.description})
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
		mail.send(msg)
		return "sent"

def notifyToOne(sender, user, category, subject=None):
	print("notifToOne")
	senderType = findType(sender)
	if senderType == None:
		return
	print(user.get("notification_accept"))
	if user.get("notification_accept") == 0:
		return
	elif user.get("notification_accept") == 1 or user.get("notification_accept") == 3:
		push = NotificationPush()
		push.sendNotif(sender, senderType, category, subject, user)
	if user.get("notification_accept") == 2 or user.get("notification_accept") == 3:
		email = NotificationEmail()
		email.sendNotif(sender, senderType, category, subject, user)

def findType(doc):
	if isinstance(doc, User):
		return "user"
	elif isinstance(doc, Orga):
		return "organization"
	elif isinstance(doc, Project):
		return "project"
	return None