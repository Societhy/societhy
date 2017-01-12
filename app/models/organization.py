from bson import ObjectId

from mongokat import Collection, Document, find_method
from ethjsonrpc import wei_to_ether

from models.events import Event, ContractCreationEvent
from models.user import UserDocument as User
from models.contract import contracts, ContractDocument as Contract

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import toWei

from .clients import client, eth_cli

class OrganisationInitializationError(Exception):
	pass

class OrgaDocument(Document):

	def __init__(self,
				doc=None,
				mongokat_collection=None,
				fetched_fields=None,
				gen_skel=None,
				contract=None,
				owner=None):
		super().__init__(doc=doc, mongokat_collection=organizations, fetched_fields=fetched_fields, gen_skel=gen_skel)
		if contract:
			self.contract = Contract(contract, owner)
			self.contract.compile()
			self["owner"] = owner.get('eth').get('mainKey') if type(owner) is User else owner			

	def _load_contract(self):
		if self.get('contract_id'):
			self.contract = contracts.find_one({"_id": self['contract_id']})

	def deploy_contract(self, from_=None, password=None, args=[]):
		if from_ is None:
			from_ = self["owner"]
		tx_hash = self.contract.deploy(from_, password, args=args)
		bw.push_event(ContractCreationEvent(tx_hash=tx_hash, callback=self.register))
		return tx_hash

	def register(self, tx_receipt):
		self.contract["address"] = tx_receipt.get('contractAddress')
		self.contract["is_deployed"] = True
		self["contract_id"] = self.contract.save()
		self.save()

	def call(self, function):
		return self.contract.call(function)

class OrgaCollection(Collection):
	document_class = OrgaDocument

	@find_method
	def find_one(self, *args, **kwargs):
		doc = super().find_one(*args, **kwargs)
		doc._load_contract()
		return doc

organizations = OrgaCollection(collection=client.main.organizations)