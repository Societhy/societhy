"""
Model that represent an organization's project.
"""

from mongokat import Collection, Document
from .clients import client

from .contract import ContractDocument as Contract, contracts

class ProjectDocument(Document):

	contract = None
	owner = None
	members = None
	description = None
	goals = None
	balance = None
	proposals = list()
	campaigns = None
	files = None

	def __init__(self, at=None, contract=None, owner=None, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=False):
		super().__init__(doc, projects, fetched_fields, gen_skel)
		if contract:
			self.contract = Contract(contract, owner.get('account') or owner.get('address'))
			self.contract.compile()
			if at:
				self["address"] = at
				self.contract["address"] = at
		elif self.get("contract_id"):
			self._loadContracts()
		if owner:
			self["owner"] = owner.public() if issubclass(type(owner), Document) else owner

	def _loadContracts(self):
		"""
		Load the contract corresponding to the project.
		"""
		if self.get('contract_id'):
			self.contract = contracts.find_one({"_id": self['contract_id']})

	def getMemberList(self):
		"""
		Empty
		"""
		pass

	def join(self, user):
		"""
		Empty
		"""
		pass

	def leave(self, member):
		"""
		Empty
		"""
		pass

	def kill(self, from_):
		"""
		Empty
		"""
		pass

	def donate(self, from_):
		"""
		Empty
		"""
		pass

	def createCampaign(self, campaign, from_):
		"""
		Empty
		"""
		pass

	def endCampaign(self, campaign):
		"""
		Empty
		"""
		pass

	def createProposal(self, proposal):
		"""
		Empty
		"""
		pass

	def killProposal(self, proposal):
		"""
		Empty
		"""
		pass

	def transferOwnership(self, from_, to_):
		"""
		Empty
		"""
		pass

class ProjectCollection(Collection):

	document_class = ProjectDocument

	def lookup(self, query):
		results = list(super().find({"name": query}, ["_id", "name", "address"]))
		for doc in results:
			doc.update({"category": "organization"})
		return results

projects = ProjectCollection(collection=client.main.projects)