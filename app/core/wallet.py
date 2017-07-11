"""
module that controls all the wallet related features
"""

import requests

from ethjsonrpc import wei_to_ether

from models.clients import eth_cli


def refreshAllBalances(user):
	"""
	user : UserDoc
	reloads all the balances of a user retrieving the current data of the blockchain
	"""
	accounts = user.get('eth').get('keys', {})
	ret = dict()
	for account in accounts.keys():
		ret[account] = wei_to_ether(eth_cli.eth_getBalance(account))
	return {
		"data": ret,
		"status": 200
	}

def refreshBalance(user, account=None):
	"""
	user : UserDoc
	account : 20bytes of the address we want to retrieve the balance from
	returns the current balance of a given account or the main one
	returns an error if account is specified and not owned by the user
	"""
	if account is None or account in user.get('eth').get('keys').keys():
		balance = user.refreshBalance(address=account)
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
	"""
	from_ : address of the sender
	to_ : address of the recipient
	amount : value of the transfer, in wei (1O*-18)
	local : boolean indicating the context
	password : password for unlocking the account
	"""
	if not local:
		ret = from_.unlockAccount(password=password)
		ret = eth_cli.transfer(from_.get('account'), to_, amount)	
		return {
			"data": ret,
			"status": 200
		}


def getTxHistory(user, account):
	"""
	user : UserDoc
	account : address 
	Retrieves the transaction history for a given address using etherchain api
	Returns the json response.
	"""
	# r = requests.get('https://etherchain.org/api/account/%s/tx/0' % account)
	print("REQUESTING : ", "https://etherchain.org/api/account/0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8/tx/0")
	r = requests.get('https://etherchain.org/api/account/0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8/tx/0')
	data = r.json().get('data') if r else None
	return {
			"data": data,
			"status": 200
		}


