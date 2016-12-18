import pytest
import time
from os import environ, listdir, path, remove

from core.blockchain_watcher import blockchain_watcher as bw
from core import keys


from models.user import users

from pymongo import MongoClient
from ethjsonrpc import ParityEthJsonRpc

print("INITIALIZING TESTS")
keyDirectory = environ.get('KEYS_DIRECTORY')
for keyFile in listdir(keyDirectory):
	if keyFile.startswith("UTC"):
		remove(path.join(keyDirectory, keyFile))
		print("removed", keyFile)

users.delete_many({})

test_user = {
	"name": "basic",
	"eth": {
		"mainKey": None,
		"keys": {}
	}
}
test_miner = {
	"name": "miner",
	"eth": {
		"mainKey": None,
		"keys": {}
	}
}

users.insert_one(test_user)
users.insert_one(test_miner)

test_miner = users.find_one({"name": "miner"})
with open(path.join(keyDirectory, 'test_key.key'), 'rb') as f:
	keys.import_new_key(test_miner, f)

@pytest.fixture(scope='module')
def app():
	from app.app import app
	app.config["TESTING"] = True
	return app.test_client()

@pytest.fixture(scope='module')
def user():
	return users.find_one({"name": "basic"})

@pytest.fixture(scope='module')
def miner():
	return users.find_one({"name": "miner"})
