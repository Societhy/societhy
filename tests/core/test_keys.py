import pytest
import json
from os import path

from core import keys

from models.user import users
from models.db import eth_cli

from tests.fixtures import *

def test_gen_base_key():
	key = keys.gen_base_key()
	assert len(key.get('address')) == 42
	assert key.get('file') is not None

def test_gen_linked_key(user):
	ret = keys.gen_linked_key(user, "test")
	user.update()
	assert ret.get('data') in user.get('eth').get('keys')
	assert eth_cli.eth_getBalance(ret.get('data')) == 0

def test_key_was_generated(user):
	address = "0xeb3daa0106891a94af2e0b70ffe839520be8fc69"
	ret = keys.key_was_generated(user, address)
	user.update()
	assert address in user.get('eth').get('keys')

def test_import_new_key(user):
	keyDirectory = '/societhy/tests/fixtures'

	with open(path.join(keyDirectory, 'test_key.key'), 'r') as f:
		data = json.load(f)
		assert data.get('address') == "5d8d77e9933279d6896eba0c08a3ec658168fcdb"
		f.close()
		f =  open(path.join(keyDirectory, 'test_key.key'), 'rb')
		ret = keys.import_new_key(user, f)
		user.update()
		assert ret.get('status') == 200
		assert ret.get('data').get('address')in user.get('eth').get('keys')

		f =  open(path.join(keyDirectory, 'test_key.key'), 'rb')
		ret = keys.import_new_key(user, f)
		assert ret.get('status') == 400
		assert ret.get('data') == "trying to import an existing key"

		f =  open(path.join(keyDirectory, 'test_wrong_key.key'), 'rb')
		ret = keys.import_new_key(user, f)
		assert ret.get('status') == 400
		assert ret.get('data') == "key format not recognized"

def test_export_key(user):
	address = "0xeb3daa0106891a94af2e0b70ffe839520be8fc69"
	ret = keys.export_key(user, address)
	assert ret is not None
	assert address in user.get('eth').get('keys')

def test_export_and_delete_key(user):
	addresses = list(user.get('eth').get('keys').keys())
	for address in addresses:
		assert address in user.get('eth').get('keys')
		ret = keys.export_key(user, address, delete=True)
		assert address not in user.get('eth').get('keys')

	ret = keys.export_key(user, "0xeb3daa0106891a94af2e0b70ffe839520be8fc69", delete=True)
	assert ret.get('status') == 400
