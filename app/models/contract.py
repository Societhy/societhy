from os import path

from mongokat import Collection, Document

from models.user import UserDocument as User
from .clients import client, eth_cli

from rlp.utils import encode_hex
from ethereum._solidity import compile_file, get_solidity
from ethereum.abi import encode_abi

class ContractDocument(Document):

	contract_directory = "/societhy/app/contracts"
	evm_code = None
	abi = None
	name = None
	address = None
	owner = None
	balance = None
	tx_history = list()

	def __init__(self,
				contract=None,
				owner = None,
				doc=None,
				mongokat_collection=None,
				fetched_fields=None,
				gen_skel=None):
		super().__init__(doc, contracts, fetched_fields, gen_skel)
		if contract:
			self["is_deployed"] = False
			self["name"] = contract
			self["contract_file"] = path.join(self.contract_directory, contract + ".sol")
			self["owner"] = owner.get('eth').get('mainKey') if type(owner) is User else owner

	def compile(self):
		compiled = compile_file(self["contract_file"]).get(self["name"])
		self["evm_code"] = '0x' + compiled.get('bin_hex')
		self["abi"] = compiled.get('abi')
		for abi_item in self["abi"]:
			signature = abi_item.get('name', self["name"]) + '('
			for _input in abi_item.get('inputs'):
				if signature[-1] != '(':
					signature += ','
				signature += _input.get('type')
			signature += ')'
			abi_item["signature"] = signature

	def deploy(self, from_, password, args=[]):
		unlocked = eth_cli.personal_unlockAccount(from_, password)
		evm_code = self["evm_code"]
		if len(args):
			constructor_abi = self.get_abi("constructor")
			types = [_input.get('type') for _input in constructor_abi.get('inputs')]
			encoded_params = encode_abi(types, args)
			encoded_params_hex = encode_hex(encoded_params).decode("utf-8")
			evm_code += encoded_params_hex
		estimated_gas_cost = eth_cli.eth_estimateGas(from_address=from_, data=evm_code)
		self["creation_tx_hash"] = eth_cli.eth_sendTransaction(from_address=from_, gas=estimated_gas_cost, data=evm_code)
		return self["creation_tx_hash"]

	def get_abi(self, elem):
		for abi_item in self.get('abi'):
			if (elem == "constructor" and abi_item.get('type') == "constructor") or abi_item.get('name') == elem:
				return abi_item

	def get_balance(self):
		return eth_cli.eth_getBalance(self["contract_address"])

	def call(self, function, local=True, *args, **kwargs):

		def compute_return_types(function_name, abi):
			return_types = list()
			signature = None
			for function in abi:
				if function.get('type') == 'function' and function.get('name') == function_name:
					for _output in function.get('outputs'):
						return_types.append(_output.get('type'))
					signature = function.get('signature')
					break
			return signature, return_types

		signature, return_types = compute_return_types(function, self["abi"])
		if local is True:
			result = eth_cli.call(self["address"], signature, list(args), return_types)
		else:
			from_ = kwargs.get('from_')
			password = kwargs.get('password')
			unlocked = eth_cli.personal_unlockAccount(from_, password)
			result = eth_cli.call_with_transaction(self["address"], from_, signature, list(args))
		return result[0] if len(result) == 1 else result

	def send_tx(self, function, *args):
		pass


class ContractCollection(Collection):
	document_class = ContractDocument

contracts = ContractCollection(collection=client.main.contracts)