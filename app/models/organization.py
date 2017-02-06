from bson import ObjectId

from mongokat import Collection, Document, find_method
from ethjsonrpc import wei_to_ether

from models.events import Event, ContractCreationEvent, LogEvent, makeTopics
from models.user import users, UserDocument as User
from models.contract import contracts, ContractDocument as Contract

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import toWei, to20bytes, normalizeAddress

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
			self.contract = Contract(contract, owner.get('account'))
			self.contract.compile()
		elif self.get("contract_id"):
			self._loadContract()
		if owner:
			self["owner"] = owner

	####
	# CONTRACT SPECIFIC METHODS
	####

	def _loadContract(self):
		if self.get('contract_id'):
			self.contract = contracts.find_one({"_id": self['contract_id']})

	def deployContract(self, from_=None, password=None, args=[]):
		if from_ is None:
			from_ = self["owner"]

		if not from_.unlockAccount(password=password):
			return "Failed to unlock account"

		tx_hash = self.contract.deploy(from_.get('account'), args=args)
		bw.pushEvent(ContractCreationEvent(tx_hash=tx_hash, callbacks=self.register, users=from_))
		return tx_hash


	####
	# CALLBACKS FOR UPDATE
	####

	def register(self, tx_receipt, users=[]):
		self.contract["address"] = tx_receipt.get('contractAddress')
		self.contract["is_deployed"] = True
		self["contract_id"] = self.contract.save()
		self.save()
		resp = {"name": self["name"], "_id": str(self["_id"])}
		resp.update({"data" :{k: str(v) if type(v) == ObjectId else v for (k, v) in self.items()}})
		return resp

	def memberJoined(self, logs):
		# decode logs, find user and add its id, key, name (?) to member list
		if len(logs) == 1 and len(logs[0].get('topics')) == 2:
			address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			member = users.find_one({"account": address})
			if member:
				member.joinedOrga(self.public())
				self["members"][member.get('account')] = member.public()
				self.save_partial();
		return self["members"]

	def memberLeft(self, logs):
		# decode logs, find user and delete it from memebr list
		if len(logs) == 1 and len(logs[0].get('topics')) == 2:
			address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			member = users.find_one({"account": address})
			if address in self["members"]:
				member.leftOrga(self.public())
				del self["members"][address]
				self.save_partial();
		return self["members"]

	def newDonation(self, logs):
		print("NEW DONATION", logs)
		return logs

	def projectCreated(self, logs):
		print("NEW PROJECT == ", logs)
		return logs


	####
	# RIGHTS MANAGEMENT
	####

	def setRights(self, user, actions, rights):
		pass

	def can(self, user, action):
		# get action signature
		# get member key
		member = self.getMember(user)
		# if user is None of has no key or is not a member, check if method is public
		if member:
			self.contract.checkRight(member.get('address'))
		# call contract function with (key, sig) and return bool
		pass

	####
	# GENERIC METHODS
	####

	def public(self):
		return {
			key: self.get(key)for key in self if key in organizations.public_info
		}


	def getMember(self, user):
		if isinstance(user, User):
			account = user.get('account')
			if account in self["members"]:
				return self["members"][account]
			else:
				for member in self["members"].values():
					if user.get('_id')  == member.get('_id'):
						return member
		elif user in self["members"]:
				return self["members"][user]
		return None

	def getTotalFunds(self):
		return self.contract.getBalance()

	def getMemberList(self):
		memberAddressList = ["0x" + member.decode('utf-8') for member in self.contract.call("getMemberList")]
		memberList = users.find({"account": {"$in": memberAddressList}}, users.public_info)
		return list(memberList)

	def join(self, user, password=None, local=False):
		tx_hash = self.contract.call('join', local=local, from_=user.get('account'), args=[user.get('name')], password=password)
		if tx_hash and tx_hash.startswith('0x'):
			topics = makeTopics(self.contract.getAbi("newMember").get('signature'), user.get('account'))
			bw.pushEvent(LogEvent("newMember", tx_hash, self.contract["address"], topics=topics, callbacks=[self.memberJoined], users=user))
			return tx_hash
		else:
			return False

	def leave(self, user, password=None):
		tx_hash = self.contract.call('leave', local=False, from_=user.get('account'), password=password)
		if tx_hash and tx_hash.startswith('0x'):
			topics = makeTopics(self.contract.getAbi("memberLeft").get('signature'), user.get('account'))
			bw.pushEvent(LogEvent("memberLeft", tx_hash, self.contract["address"], topics=topics, callbacks=[self.memberLeft], users=user))
			return tx_hash
		else:
			return False

	def donate(self, user, amount, password=None):
		if toWei(user.refreshBalance()) < amount:
			return False

		user.unlockAccount(password=password)
		tx_hash = self.contract.call('donate', local=False, from_=user.get('account'), value=amount, password=password)
		if tx_hash and tx_hash.startswith('0x'):
			topics = makeTopics(self.contract.getAbi("newDonation").get('signature'), user.get('account'))
			bw.pushEvent(LogEvent("newDonation", tx_hash, self.contract["address"], topics=topics, callbacks=[user.madeDonation, self.newDonation], users=user))
			return tx_hash
		else:
			return False

	def kill(self, from_):
		return None

	def createProject(self, user, project, password=None):
		user.unlockAccount(password=password)
		tx_hash = self.contract.call('createProject', local=False, from_=user.get('account'), args=[project], password=password)

		if tx_hash and tx_hash.startswith('0x'):
			bw.pushEvent(LogEvent("newProject", tx_hash, self.contract["address"], callbacks=[self.projectCreated], users=user))
			return tx_hash
		else:
			return False

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

	orga_info = [
		""
	]

	public_info = [
		"_id",
		"name",
		"contract_id",
		"description",
		"balance",
		"social_accounts"
	]

	structure = {
		"name": str,
		"members": dict,
		"rights": dict,
		"proposals": dict,
		"projects": dict,
		"description": str,
		"owner": dict,
		"contract_id": ObjectId,
		"orga_type": str,
		"files": dict,
		"tx_history": list,
		"creation_date": str,
		"mailing_lists": dict,
		"accounting_data": str,
		"alerts": list,
		"social_accounts": dict,
		"balance": int
	}

	@find_method
	def find_one(self, *args, **kwargs):
		doc = super().find_one(*args, **kwargs)
		doc.__init__()
		return doc

organizations = OrgaCollection(collection=client.main.organizations)
