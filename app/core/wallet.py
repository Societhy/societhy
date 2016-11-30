import time
import json
import scrypt
from os import environ, listdir, path, remove
from base64 import b64decode, b64encode
from time import strftime, clock

from flask import session, request, Response
from ethjsonrpc import wei_to_ether

from models import users
from models.db import eth_cli

from rlp.utils import encode_hex

def refresh_all_balances(user):
	accounts = user.get('eth').get('keys')
	ret = dict()
	for account in accounts.keys():
		ret[account] = eth_cli.eth_getBalance(account)
	return {
		"data": ret,
		"status": 200
	}

def refresh_balance(user, account=None):
	if account in user.get('eth').get('keys').keys():
		return {
			"data": user.refresh_balance(),
			"status": 200
		}
	else:
		balance = eth_cli.eth_getBalance(account)
		return {
			"data": wei_to_ether(balance),
			"status": 200
		}



def transfer(from_, to_, local=False):
	pass


def supply(user, amount):
	pass


def get_tx_history(user, account=None):
	pass