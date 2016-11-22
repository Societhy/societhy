import time
import json
import scrypt
from os import environ, listdir, path, remove
from base64 import b64decode, b64encode
from time import strftime, clock

from flask import session, request, Response
from ethjsonrpc import wei_to_ether

from ..models import users
from ..models.db import eth_cli

from rlp.utils import encode_hex

def refresh_balance(user, account=None):
	if account is not None and account != user.get('eth').get('mainKey'):
		balance = eth_cli.eth_getBalance(account)
		refreshedUser = users.find_one({"eth.mainKey": account})
		if refreshedUser:
			refreshedUser["balance"] = balance
			refreshedUser.save_partial()
			return wei_to_ether(balance)
	else:
	 return user.refresh_balance()


def transfer(from_, to_):
	pass


def supply(user, amount):
	pass


def get_tx_history(user, account=None):
	pass