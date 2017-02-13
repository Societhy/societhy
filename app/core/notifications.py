from app import mail

from flask_mail import Message
from models.user import users, UserDocument as User
from models.project import projects, ProjectDocument as Project
from models.organization import organizations, OrgaDocument as Orga
from models.notification import notifications, NotificationDocument as Notification
import datetime


#db.users.update({"_id" : ObjectId("5876417fcba72b00a03cf9f4")}, {$set: {"notifications" : [{"_id" : ObjectId("588a36371179f010917d4579")}]} })

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
			notifications.insert({"userId" : user.get("_id"), "sender": { "senderId": sender.get("_id"), "senderType": senderType}, "subjectId":subject.get("_id"), "category":category, "date": datetime.datetime.now(), "description":self.description})
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
	print(sender.get("_id"))
	sendType = findSenderType(sender)
	if sendType == None:
		return
	print(user.get("notification_accept"))
	if user.get("notification_accept") == 0:
		return
	elif user.get("notification_accept") == 1 or user.get("notification_accept") == 3:
		push = NotificationPush()
		push.sendNotif(sender, findSenderType(sender), category, subject, user)
	if user.get("notification_accept") == 2 or user.get("notification_accept") == 3:
		email = NotificationEmail()
		email.sendNotif(sender, findSenderType(sender), category, subject, user)

def findSenderType(sender):
	if isinstance(sender, User):
		return "user"
	elif isinstance(sender, Orga):
		print('orga')
		return "organization"
	elif isinstance(sender, Project):
		return "project"
	return None
