from os import environ

from pymongo import MongoClient

from ethjsonrpc import ParityEthJsonRpc

ip = environ.get('MONGOIP')
client = MongoClient(host=ip if ip is not None else '127.0.0.1')

eth_cli = ParityEthJsonRpc('163.5.84.117', 8080)