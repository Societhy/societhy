from datetime import datetime
from flask_socketio import SocketIO, send, emit

socketio = SocketIO()

@socketio.on('connect', namespace='/chat')
def connect():
    emit('send_message', "Salut toi", namespace='/chat')

@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!A user disconnected!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

@socketio.on('send_message', namespace='/chat')
def handle_message(data):
    message = {'avatar': data['avatar'],
        'date': data['date'],
        'content': data['content'],
        'idUser': data['idOther'], #Invert data['idOther']
        'idOther': data['idUser'] #with data['idUser']
    }
    emit('send_message', message, namespace='/chat')

@socketio.on('join', namespace='/chat')
def joined_chat(data):
    emit('send_message', {
        'idOther': data['id'],
        'idUser': data['otherId'],
        'content': 'Welcome back ' + data['name'] + '!',
        'date': datetime.utcnow().isoformat() + 'Z',
        'avatar': "static/assets/images/default-user.png"
    }, namespace='/chat')
