from os import environ

from pymongo import MongoClient

ip = environ.get('MONGOIP')
client = MongoClient(host=ip if ip is not None else '127.0.0.1')