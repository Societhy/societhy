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
	assert tx_hash.startswith('0x')
	bw.waitEvent("newMember")
	bw.pause()

def test_memberlist(miner, testOrga):
	result = testOrga.get_member_list()
	assert result != None
	print('result = ', result)