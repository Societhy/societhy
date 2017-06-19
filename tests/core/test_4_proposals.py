import pytest
from time import sleep
from bson import objectid, errors, json_util

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import *

from core import base_orga

from tests.fixtures import *

from ethjsonrpc import wei_to_ether

password = "simon"

def test_create_offer(miner, user, testOrga):
	test_offer_1 = {
	'name': 'test_offer_1',
	'client': testOrga.get('address'),
	'contractor': user.get('account'),
	"description": "Raw denim you probably haven't heard of them jean shorts Austin. Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui",
	'initialWithdrawal': 100,
	'recurrentWithdrawal': 300,
	'isRecurrent': True,
	'duration': 10,
	"type": "investment",
	'actors': ["Ox87dhdhdhdhd", "0xcou!s796kld00lkdnld", "0xsalutcava98078"]
	}
	test_offer_2 = {
	'name': 'test_offer_2',
	'client': testOrga.get('address'),
	'contractor': user.get('account'),
	"description": "Raw denim you probably haven't heard of them jean shorts Levis. Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui",
	'initialWithdrawal': 10,
	'recurrentWithdrawal': 200,
	'isRecurrent': True,
	'duration': 12,
	"type": "employment",
	'actors': ["Ox87dhdhdhdhd", "0xcou!s796kld00lkdnld", "0xsalutcava98078"]
	}
	len_prev_proposals = len(testOrga.get('proposals'))
	for index, offer in enumerate([test_offer_1, test_offer_2]):

		ret = base_orga.createOffer(miner, password, testOrga.get('_id'), offer)
		assert ret.get('status') == 200	
		assert ret.get('data') != None

		bw.waitTx(ret.get('data'))
		testOrga.reload()
		assert len(testOrga.get('proposals')) == len_prev_proposals + index + 1

def test_create_proposal(miner, testOrga):
	for index, proposal in enumerate([x for x in testOrga.get('proposals').values() if x.get('status') == 'pending']):
		assert proposal.get('status') == "pending"
		ret = base_orga.createProposal(miner, password, testOrga.get('_id'), proposal.get('offer').get('address'))
		assert ret.get('status') == 200	
		assert ret.get('data') != None
		bw.waitTx(ret.get('data'))
		testOrga.reload()
		new_proposal = testOrga.get('proposals').get(proposal.get('offer').get('address'))
		assert len(testOrga.get('proposals')) == 2
		assert new_proposal.get('from') == miner.get('account')
		assert new_proposal.get('status') == "debating"
		assert new_proposal.get('offer').get('votingDeadline') != None

def test_vote_proposal_win(miner, user, testOrga):
	NAY = 0
	YEA = 1
	for index, proposal in enumerate([x for x in testOrga.get('proposals').values() if x.get('status') == 'debating']):
		ret = base_orga.voteForProposal(miner, password, testOrga.get('_id'), proposal.get('proposal_id'), YEA if index % 2 == 0 else NAY)
		assert ret.get('status') == 200	
		assert ret.get('data') != None
		bw.waitEvent('VoteCounted')
		testOrga.reload()
		new_proposal = testOrga.get('proposals').get(proposal.get('offer').get('address'))
		assert new_proposal.get('votes_count') == 1
		assert new_proposal.get('participation') == (1 / len(testOrga.get('members'))) * 100
		assert new_proposal.get('time_left') <= 100

	last_timeleft = 100
	while len([x for x in testOrga.get('proposals').values() if x.get('status') == 'debating']) > 0:
		testOrga.refreshProposals()
		testOrga.reload()

		for index, proposal in enumerate(testOrga.get('proposals').values()):
			if proposal.get('time_left') % 10 == 0 and proposal.get('time_left') < last_timeleft:
				print("Waiting for proposal debating time to end : ", proposal.get('time_left'), "% of time left")
				last_timeleft = proposal.get('time_left')
			if proposal.get('time_left') < 0:
				assert proposal.get('status') == 'approved' if index % 2 == 0 else 'denied'
				assert proposal.get('participation') >= testOrga.get('rules').get('quorum')

# def test_vote_proposal_no_quorum(miner, user, testOrga):
# 	test_offer_3 = {
# 	'name': 'test_offer_3',
# 	'client': testOrga.get('address'),
# 	'contractor': miner.get('account'),
# 	"description": "Raw denim you probably haven't heard of them jean shorts Austin. Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui",
# 	'initialWithdrawal': 9000,
# 	'recurrentWithdrawal': 200,
# 	'isRecurrent': True,
# 	'duration': 89,
# 	"type": "investment",
# 	'actors': ["Ox87dhdhdhdhd", "0xcou!s796kld00lkdnld", "0xsalutcava98078"]
# 	}
# 	ret = base_orga.createOffer(miner, password, testOrga.get('_id'), test_offer_3)
# 	assert ret.get('status') == 200	
# 	assert ret.get('data') != None
# 	bw.waitTx(ret.get('data'))

# 	testOrga.reload()
# 	assert len(testOrga.get('proposals')) == 3

# 	for proposal in [x for x in testOrga.get('proposals').values() if x.get('status') == 'pending']:
# 		ret = base_orga.createProposal(miner, password, testOrga.get('_id'), proposal.get('offer').get('address'))
# 		assert ret.get('status') == 200	
# 		assert ret.get('data') != None
# 		bw.waitTx(ret.get('data'))
# 		testOrga.reload()
	
# 	last_timeleft = 100
# 	while len([x for x in testOrga.get('proposals').values() if x.get('status') == 'debating']) > 0:
# 		testOrga.refreshProposals()
# 		testOrga.reload()
# 		for index, proposal in enumerate([x for x in testOrga.get('proposals').values() if x.get('status') == 'debating']):
# 			if proposal.get('time_left') % 10 == 0 and proposal.get('time_left') < last_timeleft:
# 				print("Waiting for proposal debating time to end : ", proposal.get('time_left'), "% of time left")
# 				last_timeleft = proposal.get('time_left')
# 			if proposal.get('time_left') < 0:
# 				assert proposal.get('status') == 'denied'
# 				assert proposal.get('participation') <= testOrga.get('rules').get('quorum')

def test_execute_proposal(miner, testOrga):
	for p in testOrga.get('proposals').values():
		initial_balance = eth_cli.eth_getBalance(p.get('offer').get('contractor'))
		if p.get('status') == 'approved':
			ret = base_orga.executeProposal(miner, password, testOrga.get('_id'), p.get('proposal_id'))
			assert ret.get('status') == 200	
			assert ret.get('data') != None
			bw.waitTx(ret.get('data'))
			sleep(1)
			testOrga.reload()
			assert testOrga["proposals"][p.get('offer').get('address')]["executed"] == True
			assert eth_cli.eth_getBalance(p.get('destination')) == int(p.get('value')) - int(p.get('offer').get('initialWithdrawal'))
			assert eth_cli.eth_getBalance(p.get('offer').get('contractor')) == initial_balance + int(p.get('offer').get('initialWithdrawal'))


def test_withdraw_funds_from_offer(miner, user, testOrga):
	for p in testOrga.get('proposals').values():
		initial_balance = eth_cli.eth_getBalance(p.get('offer').get('contractor'))
		if p.get('status') == 'approved' and p.get('executed') is True:
			for _ in range(5):
				ret = base_orga.withdrawFundsFromOffer(user, password, testOrga.get('_id'), p.get('offer').get('contract_id'))
				initial_balance -= 2303750000000000 # remove gas cost
				assert ret.get('status') == 200
				assert ret.get('data') != None
				if ret.get('status') == 200:
					bw.waitTx(ret.get('data'))
				assert initial_balance <= eth_cli.eth_getBalance(p.get('offer').get('contractor')) <= initial_balance + int(p.get('offer').get('dailyWithdrawalLimit'))
	bw.stop()

