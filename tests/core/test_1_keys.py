import pytest
import json
from os import path

from core import keys

from models.user import users
from models.clients import eth_cli

from tests.fixtures import *

def test_genBaseKey(miner):
	mockTx(nb=1)
	while miner.refreshBalance() < 1:
		bw.waitBlock()
	key = keys.genBaseKey("test")
	assert len(key.get('address')) == 42
	assert key.get('file') is not None

def test_genLinkedKey(user):
	ret = keys.genLinkedKey(user, "test")
	user.update()
	address = ret.get('data')
	assert address in user.get('eth').get('keys')
	assert eth_cli.eth_getBalance(address) == 0
	user.setDefaultKey(address)
	assert user.unlockAccount(password="test") == True

def test_keyWasGenerated(user):
	address = "0xeb3daa0106891a94af2e0b70ffe839520be8fc69"
	ret = keys.keyWasGenerated(user, address)
	user.update()
	assert address in user.get('eth').get('keys')

def test_set_default_key(user):
	address = "0xeb3daa0106891a94af2e0b70ffe839520be8fc69"

	assert user.get('account') == user.getKey()
	assert user.getKey() != address
	user.setDefaultKey(address)
	assert user.getKey() == address

def test_importNewKey(user):
	keyDirectory = '/societhy/tests/fixtures'

	with open(path.join(keyDirectory, 'test_key.key'), 'r') as f:
		data = json.load(f)
		assert data.get('address') == "5d8d77e9933279d6896eba0c08a3ec658168fcdb"
		f.close()
		f =  open(path.join(keyDirectory, 'test_key.key'), 'rb')
		ret = keys.importNewKey(user, f)
		user.update()
		assert ret.get('status') == 200
		assert ret.get('data').get('address')in user.get('eth').get('keys')
		
		user.setDefaultKey("0x5d8d77e9933279d6896eba0c08a3ec658168fcdb")
		assert user.unlockAccount(password="simon")

		f =  open(path.join(keyDirectory, 'test_key.key'), 'rb')
		ret = keys.importNewKey(user, f)
		assert ret.get('status') == 400
		assert ret.get('data') == "trying to import an existing key"

		f =  open(path.join(keyDirectory, 'test_wrong_key.key'), 'rb')
		ret = keys.importNewKey(user, f)
		assert ret.get('status') == 400
		assert ret.get('data') == "key format not recognized"

def test_exportKey(user):
	address = "0xeb3daa0106891a94af2e0b70ffe839520be8fc69"
	ret = keys.exportKey(user, address)
	assert ret is not None
	assert address in user.get('eth').get('keys')

def test_export_and_delete_key(user):
	addresses = list(user.get('eth').get('keys').keys())
	for address in addresses:
		assert address in user.get('eth').get('keys')
		ret = keys.exportKey(user, address, delete=True)
		assert address not in user.get('eth').get('keys')

	ret = keys.exportKey(user, "0xeb3daa0106891a94af2e0b70ffe839520be8fc69", delete=True)
	assert ret.get('status') == 400
