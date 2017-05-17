import pytest
from time import sleep
from bson import objectid, errors, json_util

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import *

from core import base_orga

from tests.fixtures import *

from ethjsonrpc import wei_to_ether

password = "simon"

def test_create_offer(miner, testOrga):
	test_offer = {
	'client': testOrga.get('address'),
	'contractor': miner.get('account'),
	'hashOfTheProposalDocument': "0xc9770dac2bf785ed180884898b10c7f245ef231dba0711e92b681bb31752b389",
	'totalCost': 100,
	'initialWithdrawal': 50,
	'minDailyWithdrawalLimit': 1,
	'payoutFreezePeriod': 0,
	'isRecurrent': False,
	'duration': 0
	}
	ret = base_orga.createOffer(miner, password, testOrga.get('_id'), test_offer)
	assert ret.get('status') == 200	
	assert ret.get('data') != None

	bw.waitEvent('OfferCreated')
