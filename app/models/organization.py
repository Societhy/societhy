from bson import ObjectId

from mongokat import Collection, Document, find_method
from ethjsonrpc import wei_to_ether

from models.events import Event, ContractCreationEvent, LogEvent, make_topics
from models.user import users, UserDocument as User
from models.contract import contracts, ContractDocument as Contract

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import toWei

from .clients import client, eth_cli

class OrganisationInitializationError(Exception):
	pass

class OrgaDocument(Document):

	contract = None
	rules = None
	members = dict()
	files = dict()
	projects = dict()
	proposals = dict()
	social_links = None
	shares = None
	alerts = None

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

	# CONTRACT SPECIFIC METHODS

	def _load_contract(self):
		if self.get('contract_id'):
			self.contract = contracts.find_one({"_id": self['contract_id']})

	def deploy_contract(self, from_=None, password=None, args=[]):
		if from_ is None:
			from_ = self["owner"]
		tx_hash = self.contract.deploy(from_, password, args=args)
		bw.push_event(ContractCreationEvent(tx_hash=tx_hash, callbacks=self.register))
		return tx_hash

	def register(self, tx_receipt):
		self.contract["address"] = tx_receipt.get('contractAddress')
		self.contract["is_deployed"] = True
		self["contract_id"] = self.contract.save()
		self.save()

	# CALLBACKS FOR UPDATE

	def memberJoined(self, logs):
		# decode logs, find user and add its id (?) to member list
		print("USER JOINED", logs)

	def memberLeft(self, logs):
		# decode logs, find user and delete it from memebr list
		print("USEF LEFT", logs)

	def newDonation(self, logs):
		print("NEW DONATION", logs)

	# GENERIC METHODS

	def getTotalFunds(self):
		return self.contract.get_balance()

	def get_member_list(self):
		memberAddressList = ["0x" + member.decode('utf-8') for member in self.contract.call("getMemberList")]
		memberList = users.find({"eth.mainKey": {"$in": memberAddressList}})
		return list(memberList)

	def join(self, user, password=None):
		from_ = user.get('eth').get('mainKey')
		tx_hash = self.contract.call('join', local=False, from_=from_, password=password, args=[user.get('name')])
		if tx_hash.startswith('0x'):
			topics = make_topics(self.contract.get_abi("newMember").get('signature'), from_)
			bw.push_event(LogEvent("newMember", self.contract["address"], topics=topics, callbacks=[user.joinedOrga, self.memberJoined]))
			print ("tx hash ok with ", tx_hash)
			return tx_hash
		else:
			return False

	def leave(self, user, password=None):
		from_ = user.get('eth').get('mainKey')
		tx_hash = self.contract.call('leave', local=False, from_=from_, password=password)
		if tx_hash.startswith('0x'):
			topics = make_topics(self.contract.get_abi("memberLeft").get('signature'), from_)
			bw.push_event(LogEvent("memberLeft", self.contract["address"], topics=topics, callbacks=[user.leftOrga, self.memberLeft]))
			return tx_hash
		else:
			return False

	def donate(self, user, password=None):
		from_ = user.get('eth').get('mainKey')
		tx_hash = self.contract.call('donate', local=False, from_=from_, password=password, value=100)
		if tx_hash.startswith('0x'):
			topics = make_topics(self.contract.get_abi("newDonation").get('signature'), from_)
			bw.push_event(LogEvent("newDonation", self.contract["address"], topics=topics, callbacks=[user.madeDonation, self.newDonation]))
			return tx_hash
		else:
			return False

	def kill(self, from_):
		return None

	def createProject(self, project):
		return None

	def killProject(self, project):
		return None

	def createProposal(self, proposal):
		return None

	def killProposal(self, proposal):
		return None

	def transferOwnership(self, from_, to_):
		return None


class OrgaCollection(Collection):
	document_class = OrgaDocument

	@find_method
	def find_one(self, *args, **kwargs):
		doc = super().find_one(*args, **kwargs)
		doc._load_contract()
		return doc

organizations = OrgaCollection(collection=client.main.organizations)