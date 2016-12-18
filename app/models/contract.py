from os import path

from mongokat import Collection, Document

from models.user import UserDocument as User
from .clients import client, eth_cli

from ethereum._solidity import compile_file, get_solidity

class ContractDocument(Document):

	contract_directory = "/societhy/app/contracts"

	def __init__(self,
				contract=None,
				owner = None,
				doc=None,
				mongokat_collection=None,
				fetched_fields=None,
				gen_skel=None):
		super().__init__(doc, contracts, fetched_fields, gen_skel)
		if contract:
			self["name"] = contract
			self["contract_file"] = path.join(self.contract_directory, contract + ".sol")
			self["owner"] = owner.get('eth').get('mainKey') if type(owner) is User else owner

	def compile(self):
		compiled = compile_file(self["contract_file"]).get(self["name"])
		self["evm_code"] = '0x' + compiled.get('bin_hex')
		self["abi"] = compiled.get('abi')

	def deploy(self, from_, password):
		unlocked = eth_cli.personal_unlockAccount(from_, password)
		estimated_gas_cost = eth_cli.eth_estimateGas(from_address=from_, data=self["evm_code"])
		self["creation_tx_hash"] = eth_cli.eth_sendTransaction(from_address=from_, gas=estimated_gas_cost, data=self["evm_code"])
		return self["creation_tx_hash"]

	def get_balance(self):
		return eth_cli.eth_getBalance(self["contract_address"])


class ContractCollection(Collection):
	document_class = ContractDocument

contracts = ContractCollection(collection=client.main.contracts)