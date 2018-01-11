from datetime import datetime

import models.organization
import models.project
import models.user

import urllib.parse

from bson.objectid import ObjectId
import json
from flask_mail import Message
from flask import render_template
from mongokat import Collection, Document

from models.clients import app
from flask_socketio import SocketIO, send, emit

from .clients import client, mail, app

descriptionDict = {
    "NewMember": " is the new member of ",
    "MemberLeft": " leave ",
    "ProposalCreated": "did a new proposition",
    "DonationMade": " give to ",
    "newSpending": " spend ",
    "newMessage": " send you a message",
    "newFriendAdd": " send you a friend request",
    "orgaCreated": "invited you to join the organisation ",
    "ProjectCreated": "created a new project ",
    "newInviteJoinOrga": " invited you to join the orga",
    "OfferCreated": " created a new offer",
    "newsPublished": " publish a news"
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
        notification = NotificationDocument()
        description = descriptionDict[category]
        if not description:
            return
        if subject:
            subjectType = type(sender).__name__
            if not subjectType:
                return
            data = {"userId": user.get("_id"),
                    "sender": {"id": sender.get("_id"), "name": sender.get("name"), "type": senderType},
                    "subject": {"id": subject.get("_id"), "type": subjectType},
                    "category": category,
                    "description": description}
            notification.push(data)
        else:
            data = {"userId": user.get("_id"),
                    "sender": {"id": sender.get("_id"), "type": senderType},
                    "category": category,
                    "description": description}
            notification.push(data)


def sendNotifEmail(sender, senderType, category, subject, user):
    """
    Insert the notification in the database in order to be sent.
    """
    description = descriptionDict[category]
    if not description:
        return None
    msg = Message(category, sender='societhycompany@gmail.com', recipients=[user.get("email")])
    if subject:
        msg.body = subject.get("name") + description + sender.get("name")
    else:
        msg.body = sender.get("name") + description
    with app.app_context():
        mail.send(msg)
    return msg


def notifyToOne(sender, user, category, subject=None):
    """
    Used to send a notification depending of the type.
    """
    senderType = type(sender).__name__
    if not senderType:
        return
    # print(user.get("notification_accept"))
    # if user.get("notification_accept") == 0:
    #	return
    # elif user.get("notification_accept") == 1 or user.get("notification_accept") == 3:
    sendNotifPush(sender, senderType, category, subject, user)
    # if user.get("notification_accept") == 2 or user.get("notification_accept") == 3:
    if user.get('email') is not None:
	    sendNotifEmail(sender, senderType, category, subject, user)


class NotificationDocument(Document):
    def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None, session=None):
        super().__init__(doc=doc, mongokat_collection=notifications, fetched_fields=fetched_fields, gen_skel=gen_skel)
        self["seen"] = False
        self["createdAt"] = int(datetime.now().timestamp())

    def save(self, force=False, uuid=False, **kwargs):
        super().save(force=force, uuid=uuid, **kwargs)
        imp = __import__('core.chat', globals(), locals(), ['Clients'], 0)
        Clients = imp.Clients
        if self["subject"]["type"] == "user":
            user = models.user.users.find_one({"_id": self["subject"]["id"]})
            if user.wantNotif(self["category"], "Web"):
                if str(self["subject"]['id']) in Clients:
                    with app.app_context():
                        emit("update_notif", "", namespace='/', room=Clients[str(self["subject"]['id'])].sessionId)
            else:
                self["seen"] = True
            if user.wantNotif(self["category"], "Mail") and "angularState" in self :
                msg = Message("Notif", sender='roman.grout@hotmail.fr',
                              recipients=[user.get("email")])
                url = "http://www.localhost:4242?redirect=true&angularState=" + urllib.parse.quote(json.dumps(self["angularState"]))
                with app.app_context():
                    print(user.get("email"))
                    msg.html = render_template('/assets/views/emailing/notification.html', name=user.get("name"),
                                               description=self["description"], url=url)
                    mail.send(msg)
        #pas touche a ce save
        self.save_partial()

    def pushNotif(data):
        notifications.insert({"subject": {"id": data["subject"]["id"], "type": data["subject"]["type"]},
                              "sender": {"id": data["sender"]["id"], "type": data["sender"]["type"]},
                              "category": data["category"],
                              "createdAt": datetime.now(),
                              "date": datetime.now().strftime("%b %d, %Y %I:%M"),
                              "seen": False
                              })

    def push(self, data):
        self["user"] = {"id": None}
        self["user"]["id"] = data["userId"]
        self["category"] = data["category"]
        self["sender"] = {"id": None, "name": None, "type": None}
        self["sender"]["id"] = data["sender"]["id"]
        self["sender"]["name"] = data["sender"]["name"]
        self["sender"]["type"] = data["sender"]["type"]
        self["date"] = datetime.now().strftime("%b %d, %Y %I:%M %p")
        self["createdAt"] = datetime.now()
        self["seen"] = False
        if data["subject"]["id"]:
            self["subject"] = {"id": None, "type": None}
            self["subject"]["id"] = data["subject"]["id"]
            self["subject"]["type"] = data["subject"]["type"]
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
        data["name"] = "Unknown"
        data["addr"] = "Unknown"
        if data['type'] == 'orga':
            res = models.organization.organizations.find_one({"_id" : data['id']}, {"name": 1, "address": 1})
            data["name"] = res["name"]
            data["addr"] = res["address"]
        elif data['type'] == 'user':
            res = models.user.users.find_one({"_id" : data['id']}, {"name": 1, "account": 1 })
            if res != None:
                data["name"] = res["name"]
                data["addr"] = res["account"]
        else:
            data["name"] = "Unknown"
            data["addr"] = "Unknown"
        return data

    def getHisto(_id, date):
        data = notifications.find({
            "$and" : [
                {"$or" : [
                    {"sender.type": "orga", "sender.id" : ObjectId(_id)},
                    {"subject.type": "orga", "subject.id" : ObjectId(_id)}
                ]},
                { "createdAt" : {
                     "$gte" : datetime.strptime(date['begin'], "%b %d, %Y %H:%M"),
                     "$lt": datetime.strptime(date['end'], "%b %d, %Y %H:%M")
                }}
            ]}, {"_id": 0, "createdAt": 0})
        res = {}
        i = 0
        if data.count() != 0:
            for record in data:
                name = ""
                res[i] = record
                res[i]['sender'] = NotificationDocument.getName(record['sender'])
                res[i]['subject'] = NotificationDocument.getName(record['subject'])
                if record["category"] == "orgaCreated":
                    res[0]["first"] = record["date"]
                i = i + 1
            return res
        return []

    def getSubject(self):
        return users.find_one({"_id": self["subjectId"]})


class NotificationCollection(Collection):
    document_class = NotificationDocument
    descriptions = descriptionDict


notifications = NotificationCollection(collection=client.main.notifications)
