from os import environ

from pymongo import MongoClient
from ethjsonrpc import ParityEthJsonRpc

mongo_ip = environ.get('MONGOIP')
client = MongoClient(host=mongo_ip or '127.0.0.1')
client.main.authenticate('dev', 'SecurityIsABitBetter')

eth_ip = environ.get('ETHIP')
eth_port = environ.get('ETHPORT')
eth_cli = ParityEthJsonRpc(eth_ip or '163.5.84.117', eth_port or 8080)
