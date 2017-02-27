from bson import ObjectId

from mongokat import Collection, Document, find_method
from ethjsonrpc import wei_to_ether

from models.events import Event, ContractCreationEvent, LogEvent, makeTopics
from models.user import users, UserDocument as User
from models.contract import contracts, ContractDocument as Contract
from models.project import ProjectDocument, ProjectCollection
from models.member import Member

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import fromWei, toWei, to20bytes, normalizeAddress

from .clients import client, eth_cli

class OrganisationInitializationError(Exception):
	pass

governances = ["democracy", "entreprise", "association", "private"]

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

	rules = {
		"governance": "democracy",
		"default_proposal_duration": 48,
		"quorum": 20,
		"majority": 50,
		"can_be_removed": True,
		"shareable": True,
		"public": True,
		"anonymous": False
	}

	rights = {
		"owner": {
			"join": False,
			"leave": True,
			"donate": True,
			"create_project": True,
			"create_roposal": True,
			"vote_proposal": True,
			"recruit": True,
			"remove_members": True,
			"sell_share": True,
			"buy_share": True,
		},
		"admin": {},
		"partner": {},
		"member": {
			"join": False,
			"leave": True,
			"donate": True,
			"create_project": False,
			"create_roposal": False,
			"vote_proposal": True,
			"recruit": False,
			"remove_members": False,
			"sell_share": True,
			"buy_share": True,
		},
		"default": {
			"join": True,
			"leave": False,
			"donate": True,
			"create_project": False,
			"create_roposal": False,
			"vote_proposal": False,
			"recruit": False,
			"remove_members": False,
			"sell_share": False,
			"buy_share": False,
		}
	}

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
			self["owner"] = owner.public() if isinstance(owner, User) else owner

	####
	# CONTRACT SPECIFIC METHODS
	####

	def _loadContract(self):
		if self.get('contract_id'):
			self.contract = contracts.find_one({"_id": self['contract_id']})
			balance = self.getTotalFunds()
			if balance != self["balance"]:
				self["balance"] = balance
				self.save_partial()

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
		self["address"] = tx_receipt.get('contractAddress')
		self.contract["is_deployed"] = True
		self["balance"] = self.getTotalFunds()
		self["contract_id"] = self.contract.save()

		self["rules"] = self.rules
		self.save()

		resp = {"name": self["name"], "_id": str(self["_id"])}
		resp.update({"data" :{k: str(v) if type(v) == ObjectId else v for (k, v) in self.items()}})
		return resp

	def memberJoined(self, logs):
		if len(logs) == 1 and len(logs[0].get('topics')) == 2 and len(logs[0]["decoded_data"]) == 1:
			address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			new_member = users.find_one({"account": address})
			if new_member and new_member.get('account') not in self["members"]:
				rights_tag = logs[0]["decoded_data"][0]
				if rights_tag in self.rights.keys():
					public_member =  Member(new_member.public(), rights=self.rights.get(rights_tag), tag=rights_tag)
					self["members"][new_member.get('account')] = public_member
					self.save_partial();
					return { "orga": self.public(public_members=True), "rights": public_member.get('rights')}
		return False

	def memberLeft(self, logs):
		if len(logs) == 1 and len(logs[0].get('topics')) == 2:
			address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			member = self.getMember(address)
			if member:
				del self["members"][address]
				self.save_partial();
				return { "orga": self.public(public_members=True), "rights": self.rights.get('default')}
		return False

	def newDonation(self, logs):
		if len(logs) == 1 and len(logs[0].get('topics')) == 3:
			donation_amount = fromWei(int(logs[0].get('topics')[2], 16))
			self["balance"] = self.getTotalFunds()

			address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			member = self.getMember(address)
			if member:
				self["members"][address]["donation"] = member.get('donation', 0) + donation_amount
			self.save_partial()
			return self["balance"]
		return False

	def projectCreated(self, logs):
		if len(logs) == 1 and len(logs[0].get('topics')) == 2:
			contract_address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			new_project = ProjectDocument(at=contract_address, contract='basic_project', owner=self)
			if len(logs[0]["decoded_data"]) == 1:
				new_project["name"] = logs[0]["decoded_data"][0]
			project_id = new_project.save()
			if contract_address not in self["projects"]:
				self["projects"][contract_address] = new_project
				self.save_partial()
				return self
		return False



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

	def public(self, additional_infos=None, public_members=False):
		to_be_public = organizations.public_info
		if additional_infos:
			to_be_public += additional_infos
		if public_members:
			ret = {key: self.get(key) for key in self if key in to_be_public}
			ret.update({"members":{account: {"name": member["name"],
											"_id": member["_id"],
											"account": account,
											"tag": member["tag"]} for account, member in self.get('members').items()}})
			return ret
		return {
			key: self.get(key) for key in self if key in to_be_public
		}


	def getMember(self, user):
		if isinstance(user, User):
			account = user.get('account')
			if account in self["members"]:
				return self["members"][account]
			else:
				for member in self["members"].values():
					if user.get('_id')  == member.get('_id'):
						return Member(member)
		elif type(user) is str and user in self["members"]:
				return self["members"][user]
		return None

	def getTotalFunds(self):
		return fromWei(self.contract.getBalance())

	def getMemberList(self):
		memberAddressList = ["0x" + member.decode('utf-8') for member in self.contract.call("getMemberList")]
		memberList = users.find({"account": {"$in": memberAddressList}}, users.public_info)
		return list(memberList)

	def join(self, user, tag, password=None, local=False):
		tx_hash = self.contract.call('join', local=local, from_=user.get('account'), args=[user.get('name'), tag], password=password)
		if tx_hash and tx_hash.startswith('0x'):
			topics = makeTopics(self.contract.getAbi("newMember").get('signature'), user.get('account'))
			bw.pushEvent(LogEvent("newMember", tx_hash, self.contract["address"], topics=topics, callbacks=[self.memberJoined, user.joinedOrga], users=user, event_abi=self.contract["abi"]))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def leave(self, user, password=None):
		tx_hash = self.contract.call('leave', local=False, from_=user.get('account'), password=password)
		if tx_hash and tx_hash.startswith('0x'):
			topics = makeTopics(self.contract.getAbi("memberLeft").get('signature'), user.get('account'))
			bw.pushEvent(LogEvent("memberLeft", tx_hash, self.contract["address"], topics=topics, callbacks=[self.memberLeft, user.leftOrga], users=user))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def donate(self, user, amount, password=None):
		if toWei(user.refreshBalance()) < amount:
			return False
		tx_hash = self.contract.call('donate', local=False, from_=user.get('account'), value=amount, password=password)
		if tx_hash and tx_hash.startswith('0x'):
			topics = makeTopics(self.contract.getAbi("newDonation").get('signature'), user.get('account'))
			bw.pushEvent(LogEvent("newDonation", tx_hash, self.contract["address"], topics=topics, callbacks=[user.madeDonation, self.newDonation], users=user))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def kill(self, from_):
		return None

	def createProject(self, user, project, password=None):
		tx_hash = self.contract.call('createProject', local=False, from_=user.get('account'), args=[project.get('name', 'newProject')], password=password)

		if tx_hash and tx_hash.startswith('0x'):
			bw.pushEvent(LogEvent("newProject", tx_hash, self.contract["address"], callbacks=[self.projectCreated], users=user, event_abi=self.contract["abi"]))
			user.needsReloading()
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
		"address",
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
		"rules": dict,
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
		"balance": int,
		"uploaded_documents": list
	}

	@find_method
	def find_one(self, *args, **kwargs):
		doc = super().find_one(*args, **kwargs)
		doc.__init__()
		return doc

organizations = OrgaCollection(collection=client.main.organizations)
