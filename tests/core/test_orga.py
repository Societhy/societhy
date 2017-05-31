import pytest
from time import sleep
from bson import objectid, errors, json_util

from core import wallet, keys, base_orga
from core.blockchain_watcher import blockchain_watcher as bw
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

def test_create_orga(miner):
	bw.run()
	mockTx(nb=1)
	while miner.refreshBalance() < 1:
		bw.waitBlock()

	for orga_model, contracts in governances.items():
		test_orga = {
			"name": "Societhy" + "_" + orga_model, 
			"description" : "test_description", 
			"accessibility" : "public",
			"gov_model" : orga_model,
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
		sleep(0.5)
		inserted = organizations.find_one({"_id": objectid.ObjectId(new_orga["_id"])})
		assert inserted != None
		assert inserted.get('contracts') != None
		assert inserted.board != None
		assert inserted.rules != None
		if contracts.get('registryContract'):
			assert inserted.registry != None
		if contracts.get('tokenContract'):
			assert inserted.token != None
		if contracts.get('tokenFreezerContract'):
			assert inserted.token_freezer != None
		# break

def test_join(miner, testOrga):
	ret = base_orga.joinOrga(miner, password, testOrga.get('_id'), tag='owner')
	assert ret.get('status') == 200	
	assert ret.get('data') != None

	bw.waitEvent('NewMember')
	assert miner.get('name') in [member.get('name') for member in testOrga.getMemberList()]

def test_memberlist(testOrga):
	ret = base_orga.getOrgaMemberList(None, testOrga.get('_id'))
	assert ret.get('status') == 200
	assert len(ret.get('data')) == 1
	assert ret.get('data')[0].get('name') == 'simon'

def test_donate(miner, testOrga):
	ret = base_orga.donateToOrga(miner, password, testOrga.get('_id'), {"amount":1000})
	assert ret.get('status') == 200
	assert ret.get('data') is not None
	bw.waitEvent("DonationMade")
	assert testOrga.getTotalFunds() == 1000
	

def test_hidden_orga(miner):
	pass

def test_anonymous_orga(miner):
	pass

def test_createproject(miner, testOrga):
	ret = base_orga.createProjectFromOrga(miner, password, testOrga.get('_id'), {})
	assert ret.get('status') == 200
	assert ret.get('data').startswith('0x')
	bw.waitTx(ret.get('data'))
	sleep(0.5)
	testOrga.reload()
	assert len(testOrga["projects"]) == 1

def test_leave(miner, testOrga):
	ret = base_orga.leaveOrga(miner, password, testOrga.get('_id'))
	assert ret.get('status') == 200
	assert ret.get('data').startswith('0x')
	bw.waitEvent("MemberLeft")

	assert miner.get('name') not in [member.get('name') for member in testOrga.getMemberList()]
	ret = base_orga.joinOrga(miner, password, testOrga.get('_id'), tag='owner')
	assert ret.get('status') == 200	
	assert ret.get('data') != None
	bw.waitEvent('NewMember')

def test_destroyOrga(miner, testOrga):
	pass

