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
	"description": "Raw denim you probably haven't heard of them jean shorts Austin. Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui",
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

def test_create_proposal(miner, testOrga):
	test_proposal = {
		"0xdeadbeefdeadbeef": {
		"name": "first",
		"participation": 50,
		"beneficiary": "Joseph Martin",
		"from": "0xab1393Njdjdndn8820dlnjncmc",
		"status": "denied",
		"votes_count": 176,
		"created_on": "May 03, 2017 11:42 AM"
		}
	}