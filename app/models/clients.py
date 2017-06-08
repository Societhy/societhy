from os import environ

from flask import json as flask_json, Flask
from flask_socketio import SocketIO
from flask_mail import Mail
from pymongo import MongoClient
import gridfs
import eventlet
from ethjsonrpc import ParityEthJsonRpc

from core import secret_key
from core.utils import UserJSONEncoder

# FLASK APP
app = Flask(__name__, template_folder='../web/static/', static_url_path='', static_folder='../web')
app.secret_key = secret_key
app.json_encoder = UserJSONEncoder

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'societhycompany@gmail.com'
app.config['MAIL_PASSWORD'] = 'JDacdcacdc95'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


jinja_options = app.jinja_options.copy()

jinja_options.update(dict(
	block_start_string='<%',
	block_end_string='%>',
	variable_start_string='%%',
	variable_end_string='%%',
	comment_start_string='<#',
	comment_end_string='#>'
))
app.jinja_options = jinja_options



mongo_ip = environ.get('MONGOIP')
client = MongoClient(host=mongo_ip or '127.0.0.1')
db_filesystem = gridfs.GridFS(client.main)

if mongo_ip != '127.0.0.1':
	client.main.authenticate('dev', 'SecurityIsABitBetter')

eth_ip = environ.get('ETHIP')
eth_port = environ.get('ETHPORT')
eth_cli = ParityEthJsonRpc(eth_ip or '163.5.84.117', eth_port or 8080)

eventlet.monkey_patch()

import redis
redis_cli = redis.StrictRedis(host='172.17.0.2', port=6379, db=0)
socketio = SocketIO(app, async_mode='eventlet', json=flask_json, messge_queue="redis://172.17.0.2:6379")
mail = Mail(app)
