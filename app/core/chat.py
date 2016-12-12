from flask_socketio import SocketIO, send, emit

socketio = SocketIO()

@socketio.on('connect', namespace='/chat')
def connect():
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!A user connected!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    emit('send_message', "Salut toi", namespace='/chat')

@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!A user disconnected!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

@socketio.on('send_message', namespace='/chat')
def handle_message(data):
    message = {'avatar': data[avatar],
        'date': data[date],
        'content': data[content],
        'idUser': data[idUser],
        'idOther': data[idOther]
    }
    print('Received: ' + message)
    emit('send_message', message, namespace='/chat')

@socketio.on('join', namespace='/chat')
def joined_chat(data):
    print('User joined')
    emit('send_message', {
        'idOther': data['id'],
        'idUser': data['otherId'],
        'content': 'Welcome back ' + data['name'] + '!',
        'date': datetime.utcnow().isoformat() + 'Z',
        'avatar': "static/assets/images/default-user.png"
    }, namespace='/chat')
    return 'Received join'
