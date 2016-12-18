import pytest
from time import sleep

from core import wallet, keys
from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import *

from models.user import users
from models.organization import OrgaDocument, organizations
from models.db import eth_cli

from tests.fixtures import *

from ethjsonrpc import wei_to_ether


def test_create_orga(miner):
	bw.run()
	newOrga = OrgaDocument(contract='greeter.sol', owner=miner)
	newOrga.compile()
	assert newOrga["evm_code"] == "0x606060405234610000576040516102c13803806102c1833981016040528051015b5b60008054600160a060020a03191633600160a060020a03161790555b8060019080519060200190828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061008957805160ff19168380011785556100b6565b828001600101855582156100b6579182015b828111156100b657825182559160200191906001019061009b565b5b506100d79291505b808211156100d357600081556001016100bf565b5090565b50505b505b6101d6806100eb6000396000f300606060405263ffffffff60e060020a60003504166341c0e1b5811461002f578063cfae32171461003e575b610000565b346100005761003c6100cb565b005b346100005761004b61010d565b604080516020808252835181830152835191928392908301918501908083838215610091575b80518252602083111561009157601f199092019160209182019101610071565b505050905090810190601f1680156100bd5780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b6000543373ffffffffffffffffffffffffffffffffffffffff9081169116141561010a5760005473ffffffffffffffffffffffffffffffffffffffff16ff5b5b565b604080516020808201835260008252600180548451600282841615610100026000190190921691909104601f81018490048402820184019095528481529293909183018282801561019f5780601f106101745761010080835404028352916020019161019f565b820191906000526020600020905b81548152906001019060200180831161018257829003601f168201915b505050505090505b905600a165627a7a723058207a8b51943b1a03ec3100d73664886e3c4f2b195a437b94a31df523c5b3346bf40029"
	tx_hash = newOrga.deploy(password='simon')
	assert tx_hash != None
	bw.waitTx(tx_hash)
	assert newOrga["contract_address"] != None
	assert organizations.find_one({"contract_address": newOrga["contract_address"]}) != None
	bw.pause()