import pytest
from time import sleep
from bson import objectid, errors, json_util

from core import wallet, keys, base_orga
from models.clients import blockchain_watcher as bw
from core.utils import *

from models.user import users
from models.organization import OrgaDocument, organizations
from models.orga_models import governances
from models.clients import eth_cli
from models.contract import contracts
from models.user import users

from tests.fixtures import *

from ethjsonrpc import wei_to_ether

password = "simon"

def test_create_orga(miner, user):
	with open(path.join(environ.get('KEYS_DIRECTORY'), 'test_key2.key'), 'rb') as f:
		keys.importNewKey(user, f)
	user.setDefaultKey("0x4030c937f52b45959447c5fa695bcc462695c2fa")

	initial_funds = 1000
	for orga_model, contracts in governances.items():
		test_orga = {
			"name": "Societhy" + "_" + orga_model, 
			"description" : "test_description", 
			"gov_model" : orga_model,
			"initial_funds": initial_funds,
			"rules": {
				"delegated_voting": True,
				"curators": True,
				"quorum" : 50,
				"majority": 50
			}
		}
		ret = base_orga.createOrga(miner, password, test_orga)
		tx_hash = ret.get('data').get('tx_hash')
		new_orga = ret.get('data').get('orga')
		
		assert ret.get('status') == 200
		assert tx_hash != None
		bw.waitTx(tx_hash)
		bw.waitBlock()
		sleep(0.5)
		inserted = organizations.find_one({"_id": objectid.ObjectId(new_orga["_id"])})
		assert inserted != None
		assert inserted.get('contracts') != None
		assert inserted.board != None
		assert inserted.rules != None
		assert inserted.getTotalFunds() == initial_funds
		if contracts.get('registryContract'):
			assert inserted.registry != None
		if contracts.get('tokenContract'):
			assert inserted.token != None
		if contracts.get('tokenFreezerContract'):
			assert inserted.token_freezer != None
		break

# def test_hidden_orga(miner):
# 	test_orga = {
# 		"name": "Societhy_hidden_orga",
# 		"description" : "test_description", 
# 		"gov_model" : "ngo",
# 		"rules": {
# 			"delegated_voting": True,
# 			"curators": True,
# 			"quorum" : 50,
# 			"majority": 50,
# 			"hidden": True
# 		}
# 	}
# 	ret = base_orga.createOrga(miner, password, test_orga)
# 	tx_hash = ret.get('data').get('tx_hash')
# 	new_orga = ret.get('data').get('orga')
	
# 	assert ret.get('status') == 200
# 	assert tx_hash != None
# 	bw.waitTx(tx_hash)
# 	sleep(0.5)
# 	inserted = organizations.find_one({"_id": objectid.ObjectId(new_orga["_id"])})
# 	assert inserted != None
# 	all_orgas = base_orga.getAllOrganizations()
# 	assert inserted.get('_id') not in [x['_id'] for x in all_orgas.get('data')]

# def test_anonymous_orga(miner):
# 	test_orga = {
# 		"name": "Societhy_anonymous_orga",
# 		"description" : "test_description", 
# 		"gov_model" : "ngo",
# 		"rules": {
# 			"hidden": False,
# 			"delegated_voting": True,
# 			"curators": True,
# 			"quorum" : 50,
# 			"majority": 50,
# 			"anonymous": True
# 		}
# 	}
# 	ret = base_orga.createOrga(miner, password, test_orga)
# 	tx_hash = ret.get('data').get('tx_hash')
# 	new_orga = ret.get('data').get('orga')
	
# 	assert ret.get('status') == 200
# 	assert tx_hash != None
# 	bw.waitTx(tx_hash)
# 	sleep(0.5)
# 	inserted = organizations.find_one({"_id": objectid.ObjectId(new_orga["_id"])})
# 	assert inserted != None
# 	assert inserted.get('name') ==  "Societhy_anonymous_orga"
	
# 	ret = base_orga.joinOrga(miner, password, inserted.get('_id'), tag='member')
# 	assert ret.get('status') == 200
# 	assert ret.get('data') != None

# 	bw.waitEvent('NewMember')
# 	miner.reload()
# 	inserted.reload()

# 	member_list = inserted.getMemberList()
# 	assert len(miner.get('organizations')) == 1
# 	assert len([x.get('name') for x in member_list if x.get('name') is not None]) == 0
# 	assert len([x.get('account') for x in member_list]) == 1

# def test_private_orga(miner, user):
# 	test_orga = {
# 		"name": "Societhy_private_orga",
# 		"description" : "private organisation", 
# 		"gov_model" : "ngo",
# 		"rules": {
# 			"accessibility": "private",
# 			"delegated_voting": True,
# 			"curators": True,
# 			"quorum" : 50,
# 			"majority": 50,
# 		}
# 	}
# 	ret = base_orga.createOrga(miner, password, test_orga)
# 	tx_hash = ret.get('data').get('tx_hash')
# 	new_orga = ret.get('data').get('orga')
	
# 	assert ret.get('status') == 200
# 	assert tx_hash != None
# 	bw.waitTx(tx_hash)
# 	sleep(0.5)
# 	inserted = organizations.find_one({"_id": objectid.ObjectId(new_orga["_id"])})
# 	assert inserted != None
	
# 	#MINER CAN JOIN
# 	ret = base_orga.joinOrga(miner, password, inserted.get('_id'), tag='owner')
# 	assert ret.get('status') == 200	
# 	assert ret.get('data') != None
# 	bw.waitEvent('NewMember')
# 	miner.reload()
# 	assert len(miner.get('organizations')) == 2
# 	assert len([x.get('account') for x in inserted.getMemberList()]) == 1


# 	#USER CANNOT JOIN
# 	ret = base_orga.joinOrga(user, password, inserted.get('_id'), tag='member')
# 	assert ret.get('status') == 400	
# 	user.reload()
# 	assert len(user.get('organizations')) == 0
# 	assert len([x.get('account') for x in inserted.getMemberList()]) == 1

# 	#MINER ALLOW
# 	ret = base_orga.allowUserTo(miner, password, inserted.get('_id'), user.get('account'))
# 	assert ret.get('status') == 200	
# 	bw.waitTx(ret.get('data'))

# 	#USER CAN JOIN
# 	ret = base_orga.joinOrga(user, password, inserted.get('_id'), tag='member')
# 	assert ret.get('status') == 200
# 	bw.waitEvent('NewMember')
# 	user.reload()
# 	assert len(user.get('organizations')) == 1
# 	assert len([x.get('account') for x in inserted.getMemberList()]) == 2

def test_join(miner, testOrga):
	before = len(miner.get('organizations'))
	ret = base_orga.joinOrga(miner, password, testOrga.get('_id'), tag='owner')
	assert ret.get('status') == 200	
	assert ret.get('data') != None

	bw.waitEvent('NewMember')
	sleep(1)
	miner.reload()
	member_list = testOrga.getMemberList()
	assert len(miner.get('organizations')) == before + 1
	assert len(member_list) == 1
	assert miner.get('name') in [member.get('name') for member in member_list]

# def test_memberlist(testOrga):
# 	ret = base_orga.getOrgaMemberList(None, testOrga.get('_id'))
# 	assert ret.get('status') == 200
# 	assert len(ret.get('data')) == 1
# 	assert ret.get('data')[0].get('name') == 'simon'

# def test_donate(miner, testOrga):
# 	initial_balance = testOrga.getTotalFunds()
# 	ret = base_orga.donateToOrga(miner, password, testOrga.get('_id'), {"amount":1000})
# 	assert ret.get('status') == 200
# 	assert ret.get('data') is not None
# 	bw.waitEvent("DonationMade")
# 	assert testOrga.getTotalFunds() - initial_balance == 1000

# def test_leave(miner, testOrga):
# 	ret = base_orga.leaveOrga(miner, password, testOrga.get('_id'))
# 	assert ret.get('status') == 200
# 	assert ret.get('data').startswith('0x')
# 	bw.waitEvent("MemberLeft")
# 	miner.reload()

# 	assert len(miner.get('organizations')) == 2
# 	assert miner.get('name') not in [member.get('name') for member in testOrga.getMemberList()]
# 	ret = base_orga.joinOrga(miner, password, testOrga.get('_id'), tag='owner')
# 	assert ret.get('status') == 200	
# 	assert ret.get('data') != None
# 	bw.waitEvent('NewMember')

# def test_destroyOrga(miner, testOrga):
# 	pass

