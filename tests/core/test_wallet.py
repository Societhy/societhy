import pytest
from time import sleep

from core import wallet, keys
from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import *

from models.user import users
from models.clients import eth_cli

from tests.fixtures import *

from ethjsonrpc import wei_to_ether


def test_transfer(user):
	bw.resume()
	keyDirectory = '/societhy/tests/fixtures'
	to_ = keys.genBaseKey("test").get('address')
	with open(path.join(keyDirectory, 'test_key.key'), 'rb') as f:
		from_ = keys.importNewKey(user, f).get('data').get('address')
		bw.waitBlock()
		ret = wallet.transfer(user, to_, toWei(4), password="simon")
		bw.waitTx(ret.get('data'))
		assert fromWei(eth_cli.eth_getBalance(to_)) == 4

def test_refreshBalance(user):
	balance_1 = wallet.refreshBalance(user).get('data')
	bw.waitBlock()
	balance_2 = wallet.refreshBalance(user).get('data')
	assert balance_2 > balance_1

	newKey = keys.genLinkedKey(user, "test").get('data')
	balance_3 = wallet.refreshBalance(user, newKey).get('data')
	assert balance_3 == 0

	balance_4 = wallet.refreshBalance(user, "0xdeadbeefdeadbeef")
	assert balance_4.get('status') == 400
	bw.stop()