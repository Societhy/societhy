import pytest
from time import sleep
from bson import objectid, errors, json_util

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import *

from core import base_orga

from tests.fixtures import *

from ethjsonrpc import wei_to_ether

password = "simon"

test_proposal_doc = {
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

inserted = None

def test_create_offer(miner, testOrga):
	global inserted
	test_offer_1 = {
	'name': 'test_offer_1',
	'client': testOrga.get('address'),
	'contractor': miner.get('account'),
	"description": "Raw denim you probably haven't heard of them jean shorts Austin. Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui",
	'initialWithdrawal': 50,
	'isRecurrent': False,
	'duration': 0,
	"type": "investment",
	'actors': ["Ox87dhdhdhdhd", "0xcou!s796kld00lkdnld", "0xsalutcava98078"]
	}
	test_offer_2 = {
	'name': 'test_offer_2',
	'client': testOrga.get('address'),
	'contractor': miner.get('account'),
	"description": "Raw denim you probably haven't heard of them jean shorts Levis. Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui",
	'initialWithdrawal': 0,
	'recurrentWithdrawal': 200,
	'isRecurrent': True,
	'duration': 12,
	"type": "employment",
	'actors': ["Ox87dhdhdhdhd", "0xcou!s796kld00lkdnld", "0xsalutcava98078"]
	}

	ret = base_orga.createOffer(miner, password, testOrga.get('_id'), test_offer_1)
	assert ret.get('status') == 200	
	assert ret.get('data') != None

	bw.waitEvent('OfferCreated')
	testOrga.reload()
	proposals = testOrga.get('proposals')
	assert len(proposals) == 1
	inserted = next(iter(proposals.values()))

	ret = base_orga.createOffer(miner, password, testOrga.get('_id'), test_offer_2)
	assert ret.get('status') == 200	
	assert ret.get('data') != None

	bw.waitEvent('OfferCreated')
	testOrga.reload()
	proposals = testOrga.get('proposals')
	assert len(proposals) == 2

def test_create_proposal(miner, testOrga):
	global inserted
	print('---------------', inserted.get('offer').get('initialWithdrawal'), inserted.get('offer').get('dailyWithdrawalLimit'))
	test_proposal = {
		"name": "NEW KILLER PROPOSAL",
		"destination": inserted.get('offer').get('address'),
		"value": inserted.get('offer').get('initialWithdrawal') + (inserted.get('offer').get('dailyWithdrawalLimit') * 30 * inserted.get('offer').get('duration')),
	}
	ret = base_orga.createProposal(miner, password, testOrga.get('_id'), test_proposal)
	bw.waitEvent('ProposalCreated')
	testOrga.reload()
	proposals = testOrga.get('proposals')
	assert len(proposals) == 2
	new_proposal = next(iter(proposals.values()))
	assert new_proposal.get('from') == miner.get('account')
