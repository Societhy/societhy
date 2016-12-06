import pytest
import time
from os import environ

from models.user import users

from pymongo import MongoClient
from ethjsonrpc import ParityEthJsonRpc

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
