from bson import ObjectId

from mongokat import Collection, Document
from ethjsonrpc import wei_to_ether

from models.events import Event, ContractCreationEvent
from models.user import UserDocument as User
from models.contract import ContractDocument as Contract

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import toWei

from .clients import client, eth_cli

class OrgaDocument(Document):

	def __init__(self,
				contract=None,
				owner = None,
				doc=None,
				mongokat_collection=None,
				fetched_fields=None,
				gen_skel=None):
		super().__init__(doc, organizations, fetched_fields, gen_skel)
		if contract:
			self.contract = Contract(contract, owner)
			self.contract.compile()
			self["owner"] = owner.get('eth').get('mainKey') if type(owner) is User else owner

	def deploy_contract(self, from_=None, password=None):
		if from_ is None:
			from_ = self["owner"]

		tx_hash = self.contract.deploy(from_, password)
		bw.push_event(ContractCreationEvent(tx_hash=tx_hash, callback=self.register))
		return tx_hash

	def register(self, tx_receipt):
		self.contract["contract_address"] = tx_receipt.get('contractAddress')
		self["contract_id"] = self.contract.save()
		self.save()

class OrgaCollection(Collection):
	document_class = OrgaDocument

organizations = OrgaCollection(collection=client.main.organizations)