import time
import json
import requests

from ethjsonrpc import wei_to_ether

from models import users
from models.db import eth_cli


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
			"data": user.refresh_balance(account),
			"status": 200
		}
	elif not account:
		balance = eth_cli.eth_getBalance(user.get('eth').get('mainKey'))
		return {
			"data": wei_to_ether(balance),
			"status": 200
		}
	else:
		return {
			"data": "user %s does not own %s" % (user.get('id'), account),
			"status": 400
		}

def transfer(from_, to_, amount, local=False, password=None):
	if not local:
		ret = eth_cli.personal_unlockAccount(from_, password)
		ret = eth_cli.transfer(from_, to_, amount)	
		return {
			"data": ret,
			"status": 200
		}


def get_tx_history(user, account):
	# r = requests.get('https://etherchain.org/api/account/%s/tx/0' % account)
	print("REQUESTING : ", "https://etherchain.org/api/account/0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8/tx/0")
	r = requests.get('https://etherchain.org/api/account/0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8/tx/0')
	data = r.json().get('data')
	return {
			"data": data,
			"status": 200
		}


