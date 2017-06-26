"""
Model that represent an organization's project.
"""
import models.contract
import models.user
import models.events
import models.member
from models.events import ContractCreationEvent, LogEvent
from core.utils import fromWei, toWei, normalizeAddress
from mongokat import Collection, Document, find_method

from .clients import client, blockchain_watcher as bw


class ProjectDocument(Document):

	default_rules = {
		"accessibility": "public",
		"curators": False,
		"public": True,
		"hidden": False,
		"anonymous": False
	}

	default_rights = {
		"owner": {
			"join": False,
			"leave": True,
			"donate": True,
			"recruit": True,
			"remove_members": True,
		},
		"member": {
			"join": False,
			"leave": True,
			"donate": True,
			"recruit": False,
			"remove_members": False,
		},
		"default": {
			"join": True,
			"leave": False,
			"donate": False,
			"recruit": False,
			"remove_members": False,
		}
	}

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
			self.board = models.contract.ContractDocument(contract, owner.get('account') or owner.get('address'))
			self.board.compile()
			if at:
				self["address"] = at
				self.board["address"] = at

			self.default_rules.update(self["rules"])
			self["rules"] = self.default_rules
			self.default_rights.update(self["rights"])
			self["rights"] = self.default_rights

		elif len(self.get("contracts", {})) > 0:
			self._loadContracts()
		if owner:
			self["owner"] = owner.public() if issubclass(type(owner), Document) else owner

	def _loadContracts(self):
		"""
		Load the contract corresponding to the project.
		"""
		try:
			self.board = models.contract.contracts.find_one({"_id": self.get('contracts').get('board').get('_id')})
		except: pass

		try:
			self.registry = models.contract.contracts.find_one({"_id": self.get('owner').get('contracts').get('registry').get('_id')})
		except: pass


	def getMemberList(self):
		"""
		Returns a list of all members. Only the anonymous data is returned in case the 'anonymous' field has been specified.
		"""
		memberList = list(models.user.users.find({"account": {"$in": self.registry.call("getMemberListForProject", local=True, args=[self.get('address')])}}, models.user.users.anonymous_info if self.get('rules').get("anonymous") else models.user.users.public_info))
		return memberList

	def join(self, user, tag="member", password=None, local=False):
		"""
		user : UserDoc initiating the action
		tag : string used to determine the rights of the new member
		password : password unlocking the account at the origin of the action
		local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
		Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
		Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
		"""

		if not self.can(user, "join"):
			return False

		if self.get('rules').get('accessibility') == 'private':
			isAllowed = self.registry.call('isAllowed', local=True, args=[user.get('account')])
			if not isAllowed:
				return False

		tx_hash = self.registry.call('joinProject', local=local, from_=user.get('account'), args=[self.get('address'), user.get('account'), tag], password=password)
		if tx_hash and tx_hash.startswith('0x'):
			mail = {'sender':self, 'subject':user, 'users':[user], 'category':'NewMember'} if user.get('notifications').get('NewMember') else None
			bw.pushEvent(models.events.LogEvent("NewMember", tx_hash, self.registry["address"], callbacks=[self.memberJoined, user.joinedProject], users=user, event_abi=self.registry["abi"], mail=mail))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def memberJoined(self, logs, callback_data=None):
		"""
		logs : list of dict containing the event's logs
		If the transaction has succeeded and that the member isn't already part of the members, a new Member is created and stored in the orga document with its rights assigned
		The organisation is returned alongside the rights of the new member
		"""
		if len(logs) == 1 and len(logs[0].get('topics')) == 2 and len(logs[0]["decoded_data"]) == 1:
			address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			new_member = models.user.users.find_one({"account": address})
			if new_member and new_member.get('account') not in self.get('members'):
				rights_tag = logs[0]["decoded_data"][0]
				member_data = new_member.anonymous() if self.get('rules').get("anonymous") else new_member.public()
				public_member =  models.member.Member(member_data, tag=rights_tag)
				self["members"][new_member.get('account')] = public_member
				self.save_partial()
				return { "project": self, "rights": self.get('rights').get(public_member["tag"]) }

		return False

	def leave(self, user, password=None, local=False):
		"""
		Empty
		"""
		if not self.can(user, "leave"):
			return False

		tx_hash = self.registry.call('leaveProject', local=local, from_=user.get('account'), args=[self.get('address'), user.get('account')], password=password)
		if tx_hash and tx_hash.startswith('0x'):

			mail = {'sender':self, 'subject':user, 'users':[user], 'category':'MemberLeft'} if user.get('notifications').get('MemberLeft') else None
			bw.pushEvent(LogEvent("MemberLeft", tx_hash, self.registry["address"], callbacks=[self.memberLeft, user.leftProject], users=user, event_abi=self.registry["abi"], mail=mail))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def memberLeft(self, logs, callback_data=None):
		"""
		logs : list of dict containing the event's logs
		If the transaction has succeeded and that the member is part of the members, remove it
		The organisation is returned alongside the rights of the user, which is no longer a member
		"""
		if len(logs) == 1 and len(logs[0].get('topics')) == 2:
			address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			member = self.getMember(address)
			if member:
				del self["members"][address]
				self.save_partial();
				return { "orga": self.public(public_members=True), "rights": self.get('rights').get('default')}
		return False

	def kill(self, from_):
		"""
		Empty
		"""
		pass

	def donate(self, user, amount, password=None, local=False):
		"""
		user : UserDoc initiating the action
		password : password unlocking the account at the origin of the action
		local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
		Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
		Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
		"""
		if not self.can(user, "donate"):
			return False

		if toWei(user.refreshBalance()) < amount:
			return False
		tx_hash = self.board.call('donate', local=local, from_=user.get('account'), value=amount, password=password)

		if tx_hash and tx_hash.startswith('0x'):
			mail = {'sender':self, 'subject':user, 'users':[user], 'category':'DonationMade'} if user.get('notifications').get('DonationMade') else None
			bw.pushEvent(LogEvent("DonationMade", tx_hash, self.board["address"], callbacks=[user.madeDonation, self.newDonation], users=user, event_abi=self.board["abi"], mail=mail))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def newDonation(self, logs, callback_data=None):
		"""
		logs : list of dict containing the event's logs
		If the transaction has succeeded, add the amount of the donation to the member's data
		"""
		if len(logs) == 1 and len(logs[0].get('topics')) == 3:
			donation_amount = fromWei(int(logs[0].get('topics')[2], 16))
			address = normalizeAddress(logs[0].get('topics')[1], hexa=True)

			self["balance"] = self.getTotalFunds()
			member = self.getMember(address)
			if member:
				self["members"][address]["donation"] = member.get('donation', 0) + donation_amount
			self.save_partial()
			return self["balance"]
		return False


	def createPoll(self, from_, poll):
		pass

	def transferOwnership(self, from_, to_):
		"""
		Empty
		"""
		pass

	def getTotalFunds(self):
		"""
		Returns the total balance of the contract, in ether
		"""
		return fromWei(self.board.getBalance())

	def getMember(self, user):
		"""
		user : UserDoc
		Returns the member corresponding to the user passed as param, None if there is no match
		"""
		if isinstance(user, models.user.UserDocument):
			account = user.get('account')
			if account in self["members"]:
				return models.member.Member(self["members"][account])
			else:
				for member in self["members"].values():
					if user.get('_id')  == member.get('_id'):
						return models.member.Member(member)
		elif type(user) is str and user in self["members"]:
				return models.member.Member(self["members"][user])
		return None

	def can(self, user, action):
		"""
		user : userDoc
		action : string describing the action (see self.get('rights'). eg : "create_project")
		Chef if 'user' has permission to execute action 'action'.
		Returns a boolean
		"""
		member = self.getMember(user)
		if member:
			return self.get('rights').get(member.get('tag')).get(action)
		else:
			return self.get('rights').get('default').get(action)

	def public(self, additional_infos=None, public_members=False):
		"""
		additional_infos : list of all the fields we want to include in the return value
		public_members : boolean. If set to True, information about the members is returned
		Returns a public version of the document stored in db that can be read by all users
		"""

		to_be_public = projects.public_info
		if additional_infos:
			to_be_public += additional_infos
		ret = {key: self.get(key) for key in self if key in to_be_public}

		if public_members:
			ret.update({"members":{account: {"name": None if self.get('rules').get("anonymous") else member["name"],
											"_id": member["_id"],
											"account": account,
											"tag": member["tag"]} for account, member in self.get('members').items()}})
		return ret

class ProjectCollection(Collection):

	document_class = ProjectDocument

	public_info = [
		"_id",
		"address",
		"name",
		"description",
		"balance",
		"social_accounts",
		"contracts"
	]

	structure = {
		"name": str,
		"members": dict,
		"rights": dict,
		"rules": dict,
		"description": str,
		"owner": dict,
		"contracts": dict,
		"creation_date": str,
		"social_accounts": dict,
		"balance": int,
		"invited_users": list
	}

	@find_method
	def find_one(self, *args, **kwargs):
		"""
		args : see mongokat.Collection.find_one
		kwargs : see mongokat.Collection.find_one
		Overload the parent find_one function to initialize the Contract object which has its _id contained in the orga document
		"""
		doc = super().find_one(*args, **kwargs)
		if doc:
			doc.__init__()
		return doc

	def lookup(self, query):
		results = list(super().find({"name": query}, ["_id", "name", "address"]))
		for doc in results:
			doc.update({"category": "organization"})
		return results

projects = ProjectCollection(collection=client.main.projects)
