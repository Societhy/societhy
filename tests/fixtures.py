import pytest
import time
from os import environ, listdir, path, remove

from models.user import users

from pymongo import MongoClient
from ethjsonrpc import ParityEthJsonRpc

keyDirectory = environ.get('KEYS_DIRECTORY')
for keyFile in listdir(keyDirectory):
	if keyFile.startswith("UTC"):
		remove(path.join(keyDirectory, keyFile))
		print("removed", keyFile)

test_user = {
	"name": "simon",
	"eth": {
		"mainKey": None,
		"keys": {}
		}
	}
users.insert_one(test_user)

@pytest.fixture(scope='module')
def app():
	from app.app import app
	app.config["TESTING"] = True
	return app.test_client()

@pytest.fixture(scope='module')
def user():
	return users.find_one()
