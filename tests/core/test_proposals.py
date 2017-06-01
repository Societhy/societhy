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

	for index, offer in enumerate([test_offer_1, test_offer_2]):

		ret = base_orga.createOffer(miner, password, testOrga.get('_id'), offer)
		assert ret.get('status') == 200	
		assert ret.get('data') != None

		bw.waitEvent('OfferCreated')
		testOrga.reload()
		assert len(testOrga.get('proposals')) == index + 1

from pprint import pprint
def test_create_proposal(miner, testOrga):
	for index, proposal in enumerate(testOrga.get('proposals').values()):
		test_proposal = {
			"name": "NEW KILLER PROPOSAL",
			"destination": proposal.get('offer').get('address'),
			# "value": int(proposal.get('offer').get('initialWithdrawal')) + int((proposal.get('offer').get('dailyWithdrawalLimit')) * 30 * int(proposal.get('offer').get('duration'))),
		}
		# print("------------------",  proposal.get('offer').get('initialWithdrawal'), (proposal.get('offer').get('dailyWithdrawalLimit') * 30 * proposal.get('offer').get('duration')))
		ret = base_orga.createProposal(miner, password, testOrga.get('_id'), test_proposal)
		assert ret.get('status') == 200	
		assert ret.get('data') != None
		bw.waitEvent('ProposalCreated')
		testOrga.reload()
		new_proposal = testOrga.get('proposals').get(proposal.get('offer').get('address'))
		# print(new_proposal)
		assert len(testOrga.get('proposals')) == 2
		assert new_proposal.get('from') == miner.get('account')
