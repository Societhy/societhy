from datetime import datetime
from flask import Flask, request
from flask_socketio import SocketIO, send, emit

import pymongo
from bson.json_util import dumps

from models.message import messages, MessageDocument

socketio = SocketIO()

NC_Clients = {} #Not connected clients
Clients = {} #Clients connected ready to chat

class Client:
    def __init__(self, sid):
        self.sessionId = sid
        self.initialized = False
        self.id = ''

    def init(self, id):
        if self.initialized == False:
            self.id = id
            self.initialized = True
            Clients[self.id] = self

    def __repr__(self):
        return 'Id: ' + str(self.id) + ' sessionId: '+ str(self.sessionId)

@socketio.on('connect', namespace='/chat')
def connect():
    NC_Clients[request.sid] = Client(request.sid)
    emit('sessionId', request.sid, namespace='/chat', room=request.sid)

@socketio.on('disconnect', namespace='/chat')
def disconnect():
    disconnect_cli = NC_Clients.pop(request.sid, None)
    Clients.pop(disconnect_cli.id, None)

@socketio.on('send_message', namespace='/chat')
def handleMessage(data):
    message = {
        'date': data['date'],
        'data': data['content'],
        'send_address': data['idUser'],
        'recip_address': data['idOther'],
        'avatar': data['avatar'],
        'files': data['files']
    }
    if (data['idOther'] in Clients):
        emit('send_message', message, namespace='/chat', room=Clients[data['idOther']].sessionId)
    db_message = MessageDocument(message)
    db_message.save()

@socketio.on('init', namespace='/chat')
def initSocket(data):
    NC_Clients[request.sid].init(data['id'])

@socketio.on('join', namespace='/chat')
def joinedChat(data):
    last_messages = dumps(messages.find({"$or": [{'send_address': data['id'], 'recip_address': data['otherId']}, {"send_address": data['otherId'], "recip_address": data['id']}]}, {'_id': 0}).sort('_id', pymongo.ASCENDING).limit(50))
    if (data['id'] in Clients):
        emit("last_messages", last_messages, namespace='/chat', room=Clients[data['id']].sessionId)
