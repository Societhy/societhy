"""
This module handle the request for the chat features of Socethy website.
Thoses requests are special one, they are made through a SocketIO socket instead of a classic HTTP request.
SocketIO enables bidirectional communication, so the server can push data to a client without any previous request from the client.
There is in this module two global arrays, one NC_clients who contains the logged user without an open SocketIO socket, the other one Clients for the connected ones.
"""


from pymongo import ASCENDING
from datetime import datetime
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import Flask, request, json as flask_json
from flask_socketio import SocketIO, send, emit

from core.utils import UserJSONEncoder

from models import users
from models.clients import socketio
from models.message import messages, MessageDocument
from .user_management import isInContactList

NC_Clients = {} #Not connected clients
Clients = {} #Clients connected ready to chat

class Client:
    """
    This class is used to modelise the client (the user).
    It will contain the sessionId used to push request to the client from the server whithout any previous request.
    """
    def __init__(self, sid):
        """
        initialise the client's data.
        """
        self.sessionId = sid
        self.initialized = False
        self.id = ''

    def init(self, id):
        """
        initialise the client's data.
        """
        if self.initialized == False:
            self.id = id
            self.initialized = True
            Clients[self.id] = self


    def __repr__(self):
        """
        Used to print the client socket data.
        """
        return 'Id: ' + str(self.id) + ' sessionId: '+ str(self.sessionId)

@socketio.on('connect', namespace='/')
def connect():
    """
    SocketIo event triggered when a user lands on the website.
    Add it to the NotConnected Clients array if its not already in. Then send it its session id.
    """
    if not NC_Clients.get(request.sid) or NC_Clients.get(request.sid).sessionId != request.sid:
        NC_Clients[request.sid] = Client(request.sid)
        emit('sessionId', request.sid, namespace='/', room=request.sid)
    print("test")

@socketio.on('disconnect', namespace='/')
def disconnect():
    """
    SocketIo event triggered when a client disconnects.
    Remove it from the NotConnected and Connected Clients array.
    """
    disconnect_cli = NC_Clients.pop(request.sid, None)
    Clients.pop(disconnect_cli.id, None)

@socketio.on('send_message', namespace='/')
def handleMessage(data):
    """
    SocketIo event triggered when a new chat message is send by a client.
    First it add the sender client to the receiver contact list if it's not in.
    Then it emit a SocketIo event containing the message to the receiver.
    Finally it add the message on the database.
    """
    def addToContact(userId, otherId):
        contact = users.find_one({'_id': ObjectId(otherId)})
        users.update({"_id": ObjectId(userId)}, {"$addToSet": {"contact_list": {'id': str(contact['_id']), 'firstname': contact['firstname'], 'lastname': contact['lastname']}}})
        return users.find_one({'_id': ObjectId(userId)}, {'contact_list': 1, '_id': 0})

    message = {
        'date': data['date'],
        'data': data['content'],
        'send_address': data['idUser'],
        'recip_address': data['idOther'],
        'avatar': data['avatar'],
        'files': data['files']
    }
    if isInContactList(data['idOther'], data['idUser']) == False:
        contact_list = addToContact(data['idOther'], data['idUser'])
        print(dumps(contact_list))
        emit('new_contact_list', contact_list['contact_list'], namespace='/chat', room=Clients[data['idOther']].sessionId)
    if (data['idOther'] in Clients):
        emit('send_message', message, namespace='/', room=Clients[data['idOther']].sessionId)
    db_message = MessageDocument(message)
    db_message.save()

@socketio.on('notify', namespace='/')
def notify(push, sender, senderType, category, subject, user):
    if (data['idOther'] in Clients):
        notification = {
            'description': push.createDescription(category),
            'subject_name': subject['name'],
            'sender_name': sender['name']
        }
        emit('send_message', notification, namespace='/', room=Clients[data['idOther']].sessionId)
    else:
        push.sendNotif(sender, senderType, category, subject, user)


@socketio.on('init', namespace='/')
def initSocket(data):
    """
    SocketIo event triggered when a client lands on the website.
    Initializes the client.
    """
    NC_Clients[request.sid].init(data['id'])

@socketio.on('join', namespace='/')
def joinedChat(data):
    """
    SocketIo event triggered when a client choose a chat conversation.
    Takes the last 50 messages and emit it via a JSON list to the client.
    """
    last_messages = dumps(messages.find({"$or": [{'send_address': data['id'], 'recip_address': data['otherId']}, {"send_address": data['otherId'], "recip_address": data['id']}]}, {'_id': 0}).sort('_id', ASCENDING).limit(50))
    if (data['id'] in Clients):
        emit("last_messages", last_messages, namespace='/', room=Clients[data['id']].sessionId)
