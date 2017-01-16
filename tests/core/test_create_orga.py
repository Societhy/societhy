import pytest
from time import sleep

from core import wallet, keys
from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import *

from models.user import users
from models.organization import OrgaDocument, organizations
from models.clients import eth_cli
from models.contract import contracts
from models.user import users

from tests.fixtures import *

from ethjsonrpc import wei_to_ether


def test_create_orga(miner, testOrga):
	bw.run()
	while miner.refresh_balance() < 1:
		bw.waitBlock()
	tx_hash = testOrga.deploy_contract(password='simon', args=["bite"])
	assert tx_hash != None
	bw.waitTx(tx_hash)
	assert testOrga["contract_id"] != None
	testOrga = organizations.find_one({"contract_id": testOrga["contract_id"]})
	assert testOrga != None
	assert testOrga.contract != None

	bw.pause()

def test_join(miner, testOrga):
	bw.resume()
	tx_hash = testOrga.join(miner, password="simon")
	assert tx_hash is not None
	bw.waitEvent("newMember")
	bw.pause()

def test_memberlist(testOrga):
	result = testOrga.get_member_list()
	assert len(result) == 1
	assert result[0].get('name') == 'miner'

def test_donate(miner, testOrga):
	bw.resume()
	tx_hash = testOrga.donate(miner, password="simon")
	assert tx_hash is not None
	bw.waitEvent("newDonation")
	bw.pause()
	
def test_getbalance(testOrga):
	result = testOrga.getTotalFunds()
	print("result =", result)

def test_leave(miner, testOrga):
	bw.resume()
	tx_hash = testOrga.leave(miner, password='simon')
	assert tx_hash.startswith('0x')
	bw.waitEvent("memberLeft")
	bw.pause()

def test_createproject(miner, testOrga):
	pass

def test_destroyOrga(miner, testOrga):
	pass