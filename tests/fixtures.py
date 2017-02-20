import pytest
import time
from os import environ, listdir, path, remove

from core.blockchain_watcher import blockchain_watcher as bw
from core import keys


from models.user import users
from models.organization import organizations, OrgaDocument as Organization
from models.contract import contracts
from models.project import projects
from models.clients import eth_cli

from pymongo import MongoClient
from ethjsonrpc import ParityEthJsonRpc

print("INITIALIZING TESTS")
keyDirectory = environ.get('KEYS_DIRECTORY')
for keyFile in listdir(keyDirectory):
	if keyFile.startswith("UTC"):
		remove(path.join(keyDirectory, keyFile))
		print("removed", keyFile)

users.delete_many({})
organizations.delete_many({})
projects.delete_many({})
contracts.delete_many({})


test_user = {
	"name": "basic",
	"account": None,
	"eth": {
		"keys": {}
	}
}
test_miner = {
	"name": "miner",
	"account": None,
	"eth": {
		"keys": {}
	}
}

users.insert_one(test_user)
users.insert_one(test_miner)

test_miner = users.find_one({"name": "miner"})
with open(path.join(keyDirectory, 'test_key.key'), 'rb') as f:
	keys.importNewKey(test_miner, f)


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

@pytest.fixture(scope='module')
def testOrga(miner):
	return organizations.find_one({"name": "basic_orga"}
)

def mockTx(nb=5):
	for i in range(nb):
		test_miner.unlockAccount(password='simon')
		ret = eth_cli.transfer(test_miner.get('account'), "0x00a329c0648769a73afac7f9381e08fb43dbea72", 0)
		bw.waitTx(ret)

