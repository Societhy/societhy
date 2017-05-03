"""
This module implement the ContractDocument class.
This model represent the ethereum contracts that will be deployed on the blockchain.
"""

from os import path, listdir

from mongokat import Collection, Document

from models.user import UserDocument as User
from .clients import client, eth_cli

from rlp.utils import encode_hex
from ethereum._solidity import compile_file, get_solidity
from ethereum.abi import encode_abi

class ContractDocument(Document):
	"""
	Variables represents the fields in the database.
	"""
	contract_directory = "/societhy/contracts"
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
			self["contract_name"] = contract
			self["owner"] = owner.get('account') if type(owner) is User else owner

	def compile(self):
		"""
		Compile the contract from a .sol file to an ABI file.
		Then put the signature.
		"""
		solc_key = self["contract_name"] + '.sol:' + self["contract_name"]
		compiled = compile_file(self["contract_file"]).get(solc_key)
		self["evm_code"] = '0x' + compiled.get('bin_hex')
		self["abi"] = compiled.get('abi')
		for abi_item in self["abi"]:
			signature = abi_item.get('name', self["name"]) + '('
			for _input in abi_item.get('inputs', []):
				if signature[-1] != '(':
					signature += ','
				signature += _input.get('type')
			signature += ')'
			abi_item["signature"] = signature

	def deploy(self, from_, args=[]):
		"""
		from_ : emitting address.
		args = addtionals arguments.

		Deploy the contract on the blockchain.
		"""
		evm_code = self["evm_code"]
		if len(args):
			constructor_abi = self.getAbi("constructor")
			types = [_input.get('type') for _input in constructor_abi.get('inputs')]
			encoded_params = encode_abi(types, args)
			encoded_params_hex = encode_hex(encoded_params)
			evm_code += encoded_params_hex
		estimated_gas_cost = eth_cli.eth_estimateGas(from_address=from_, data=evm_code)
		self["creation_tx_hash"] = eth_cli.eth_sendTransaction(from_address=from_, gas=estimated_gas_cost, data=evm_code)
		return self["creation_tx_hash"]

	def getAbi(self, elem):
		"""
		Return the Application Binary Interface.
		"""
		for abi_item in self.get('abi'):
			if (elem == "constructor" and abi_item.get('type') == "constructor") or abi_item.get('name') == elem:
				return abi_item

	def getBalance(self):
		"""
		Return the ETH balance of the contract.
		"""
		return eth_cli.eth_getBalance(self["address"])

	def call(self, function, local=True, **kwargs):
		"""
		Used to call a specified function of a deployed contract
		"""

		def computeReturnTypes(function_name, abi):
			"""
			"""
			return_types = list()
			signature = None
			for function in abi:
				if function.get('type') == 'function' and function.get('name') == function_name:
					for _output in function.get('outputs'):
						return_types.append(_output.get('type'))
					signature = function.get('signature')
					break
			return signature, return_types

		signature, return_types = computeReturnTypes(function, self["abi"])
		if local is True:
			result = eth_cli.call(self["address"], signature, kwargs.get('args'), return_types)
		else:
			from_ = kwargs.get('from_')
			result = eth_cli.call_with_transaction(from_, self["address"], signature, kwargs.get('args'), value=kwargs.get('value'), gas=kwargs.get('gas'))
		return result[0] if len(result) == 1 else result

	def send_tx(self, function, *args):
		"""
		In developpement.
		"""
		pass


class ContractCollection(Collection):
	document_class = ContractDocument

contracts = ContractCollection(collection=client.main.contracts)
