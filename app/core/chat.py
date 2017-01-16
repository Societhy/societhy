from datetime import datetime
from flask import Flask, request
from flask_socketio import SocketIO, send, emit

socketio = SocketIO()

NC_Clients = {} #Not connected clients
Clients = {} #Clients connected ready to chat

class Client:
    def __init__(self, sid):
        self.sessionId = sid
        self.initialized = False
        self.id = ""

    def init(self, id):
        if self.initialized == False:
            self.id = id
            self.initialized = True
            Clients[self.id] = self

    def __repr__(self):
        return "Id: " + str(self.id) + " sessionId: "+ str(self.sessionId)

@socketio.on('connect', namespace='/chat')
def connect():
    NC_Clients[request.sid] = Client(request.sid)

@socketio.on('disconnect', namespace='/chat')
def disconnect():
    disconnect_cli = NC_Clients.pop(request.sid, None)
    Clients.pop(disconnect_cli.id, None)

@socketio.on('send_message', namespace='/chat')
def handle_message(data):
    message = {'avatar': data['avatar'], #change with data[avatar]
        'date': data['date'],
        'content': data['content'],
        'idUser': data['idUser'],
        'idOther': data['idOther']
    }
    emit('send_message', message, namespace='/chat', room=Clients[data['idOther']].sessionId)

@socketio.on('init', namespace='/chat')
def init_socket(data):
    NC_Clients[request.sid].init(data['id'])

@socketio.on('join', namespace='/chat')
def joined_chat(data):
    print('Joined')
    # envoyer les n messaages précedents avec la personne...
    # emit('send_message', {
    #     'idOther': data['id'],
    #     'idUser': data['otherId'],
    #     'content': 'Welcome back ' + data['name'] + '!',
    #     'date': datetime.utcnow().isoformat() + 'Z',
    #     'avatar': "static/assets/images/default-user.png"
    # }, namespace='/chat')
