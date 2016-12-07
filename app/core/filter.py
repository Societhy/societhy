import time

from models import users
from models.db import eth_cli

from . import blockFilter

from ethjsonrpc import wei_to_ether

def newBlock_then(function):
	while True:
		if len(eth_cli.eth_getFilterChanges(blockFilter)) > 0:
			break
		print("polling...", eth_cli.eth_getFilterChanges(blockFilter), "mining is", eth_cli.eth_mining(), "blocknumber = ", eth_cli.eth_blockNumber())
		sleep(1/10)
	function()

def waitBlock():
	eth_cli.eth_getFilterChanges(blockFilter)
	while True:
		if len(eth_cli.eth_getFilterChanges(blockFilter)) > 0:
			break
		print('.', end="", flush=True)
		time.sleep(1/10)
