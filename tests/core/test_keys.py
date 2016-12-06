import pytest
import json
from os import path

from core import keys

from models.user import users
from models.db import eth_cli

from tests.fixtures import *

from werkzeug.datastructures import FileStorage

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
	keyDirectory = '/societhy/utils'
	with open(path.join(keyDirectory, 'test_key.key'), 'r') as f:
		data = json.load(f)
		assert data.get('address') == "5d8d77e9933279d6896eba0c08a3ec658168fcdb"
		f.close()
		f =  open(path.join(keyDirectory, 'test_key.key'), 'rb')
		ret = keys.import_new_key(user, f)
		user.update()
		assert ret.get('status') == 200
		assert ret.get('data').get('address')in user.get('eth').get('keys')

def test_export_key(user):
	address = "0xeb3daa0106891a94af2e0b70ffe839520be8fc69"
	ret = keys.export_key(user, address)
	assert ret is not None
	assert address in user.get('eth').get('keys')

def test_export_and_delete_key(user):
	address = "0xeb3daa0106891a94af2e0b70ffe839520be8fc69"
	ret = keys.export_key(user, address, delete=True)
	assert address not in user.get('eth').get('keys')
