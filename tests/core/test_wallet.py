import pytest
from time import sleep

from core import wallet, keys, filter
from core.utils import *

from models.user import users
from models.db import eth_cli

from tests.fixtures import *

from ethjsonrpc import wei_to_ether

def test_transfer(user):
	keyDirectory = '/societhy/tests/fixtures'
	to_ = keys.gen_base_key().get('address')
	with open(path.join(keyDirectory, 'test_key.key'), 'rb') as f:
		from_ = keys.import_new_key(user, f).get('data').get('address')
		filter.waitBlock()
		ret = wallet.transfer(from_, to_, toWei(4), password="simon")
		filter.waitBlock(blockNumber=2)
		assert fromWei(eth_cli.eth_getBalance(to_)) == 4

def test_refresh_balance(user):
	balance_1 = wallet.refresh_balance(user).get('data')
	filter.waitBlock()
	balance_2 = wallet.refresh_balance(user).get('data')
	assert balance_2 > balance_1

	newKey = keys.gen_linked_key(user, "test").get('data')
	balance_3 = wallet.refresh_balance(user, newKey).get('data')
	assert balance_3 == 0

	balance_4 = wallet.refresh_balance(user, "0xdeadbeefdeadbeef")
	assert balance_4.get('status') == 400
