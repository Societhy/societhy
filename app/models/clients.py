from os import environ

from flask import json as flask_json, Flask
from flask_socketio import SocketIO
from flask_mail import Mail
from pymongo import MongoClient
import gridfs
import eventlet
import redis
from ethjsonrpc import ParityEthJsonRpc

app = Flask(__name__, template_folder='../web/static/', static_url_path='', static_folder='../web')

mongo_ip = environ.get('MONGOIP')
client = MongoClient(host=mongo_ip or '127.0.0.1')
db_filesystem = gridfs.GridFS(client.main)

if mongo_ip != '127.0.0.1':
	client.main.authenticate('dev', 'SecurityIsABitBetter')

eth_ip = environ.get('ETHIP')
eth_port = environ.get('ETHPORT')
eth_cli = ParityEthJsonRpc(eth_ip or '163.5.84.117', eth_port or 8080)

eventlet.monkey_patch(thread=True)

redis_cli = redis.StrictRedis(host='172.17.0.2', port=6379, db=0)
socketio = SocketIO(async_mode='eventlet', json=flask_json, messge_queue="redis://172.17.0.2:6379")
mail = Mail()
