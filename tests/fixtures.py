import pytest
import time
from os import environ, listdir, path, remove

from core.blockchain_watcher import blockchain_watcher as bw
from core import keys


from models.user import users, UserDocument
from models.organization import organizations, OrgaDocument as Organization
from models.contract import contracts
from models.project import projects
from models.clients import eth_cli

from pymongo import MongoClient
from ethjsonrpc import ParityEthJsonRpc
import scrypt
from rlp.utils import encode_hex

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

SALT_LOGIN_PASSWORD = "du gros sel s'il vous plait"

test_user = {
	"name": "basic",
	"password": encode_hex(scrypt.hash("test", SALT_LOGIN_PASSWORD)),
	"account": None,
	"eth": {
		"keys": {}
	},
	"notifications": {
		'NewMember': False,
		'MemberLeft': False,
		'ProposalCreated': False,
		"OfferCreated": False,
		'DonationMade': False,
		'newSpending': False,
		'newMessage': False,
		'newFriendAdd': False,
		'orgaCreated': False,
		'ProjectCreated': False,
		'newInviteJoinOrga': False
	}
}

test_miner = {
	"name": "simon",
	"password": encode_hex(scrypt.hash("test", SALT_LOGIN_PASSWORD)),
	"account": None,
	"eth": {
		"keys": {}
	},
	"notifications": {
		'NewMember': False,
		'MemberLeft': False,
		'ProposalCreated': False,
		"OfferCreated": False,
		'DonationMade': False,
		'newSpending': False,
		'newMessage': False,
		'newFriendAdd': False,
		'orgaCreated': False,
		'ProjectCreated': False,
		'newInviteJoinOrga': False
	}
}

test_user_doc = UserDocument(doc=test_user, gen_skel=True)
test_miner_doc = UserDocument(doc=test_miner, gen_skel=True)
test_user_doc.save()
test_miner_doc.save()

miner_1 = users.find_one({"name": "simon"})
with open(path.join(keyDirectory, 'test_key.key'), 'rb') as f:
	keys.importNewKey(miner_1, f)


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
	return users.find_one({"name": "simon"})

@pytest.fixture(scope='module')
def testOrga(miner):
	return organizations.find_one({"name" :'Societhy_ngo'})

def mockTx(nb=5):
	for i in range(nb):
		miner_1.unlockAccount(password='simon')
		ret = eth_cli.transfer(miner_1.get('account'), "0x00a329c0648769a73afac7f9381e08fb43dbea72", 0)
		bw.waitTx(ret)

