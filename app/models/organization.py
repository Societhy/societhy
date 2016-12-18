from os import path
from bson.objectid import ObjectId

from mongokat import Collection, Document
from ethjsonrpc import wei_to_ether

from models.events import Event, ContractCreationEvent
from models.user import UserDocument

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import toWei

from .db import client, eth_cli

class OrgaDocument(Document):

	contract_directory = "/societhy/app/contracts"

	def __init__(self, doc=None, mongokat_collection=None,
				fetched_fields=None, gen_skel=None,
				contract=None, owner=None):
		super().__init__(doc, organizations, fetched_fields, gen_skel)
		self["contract_file"] = contract
		self["owner"] = owner.get('eth').get('mainKey') if type(owner) is UserDocument else owner

	def compile(self):
		with open(path.join(self.contract_directory, self["contract_file"]), 'r') as f:
			solidity_code = f.read()
			self["evm_code"] = eth_cli.eth_compileSolidity(solidity_code)

	def deploy(self, from_=None, password=None):
		if from_ is None:
			from_ = self["owner"]

		unlocked = eth_cli.personal_unlockAccount(from_, password)
		estimated_gas_cost = eth_cli.eth_estimateGas(from_address=from_, data=self["evm_code"])
		self["creation_tx_hash"] = eth_cli.eth_sendTransaction(from_address=from_, gas=estimated_gas_cost, data=self["evm_code"], value=toWei(19))

		bw.push_event(ContractCreationEvent(tx_hash=self["creation_tx_hash"], callback=self.register))
	
		return self["creation_tx_hash"]

	def register(self, tx_receipt):
		self["contract_address"] = tx_receipt.get('contractAddress')
		self.save()

class OrgaCollection(Collection):
	document_class = OrgaDocument

organizations = OrgaCollection(collection=client.main.orgas)