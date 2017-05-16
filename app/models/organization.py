from bson import ObjectId

from mongokat import Collection, Document, find_method
from ethjsonrpc import wei_to_ether

from bson import objectid

from models.events import Event, ContractCreationEvent, LogEvent, makeTopics
from models.user import users, UserDocument as User
from models.contract import contracts, ContractDocument as Contract
from models.project import ProjectDocument, ProjectCollection
from models.member import Member
from models.notification import notifications, NotificationDocument as notification
from models.offer import Offer


from core.notifications import notifyToOne
from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import fromWei, toWei, to20bytes, to32bytes, normalizeAddress

from .clients import client, eth_cli

"""
This module implements the organization class alongside with all its methods
"""

class OrganisationInitializationError(Exception):
	pass

class OrgaDocument(Document):
	"""
	Overrides a mongokat.Document and add custom methods
	This class is used everytime a controller needs to manipulate an organisation
	"""

	board = None
	rules = None
	registry = None
	token = None
	members = dict()
	files = dict()
	projects = dict()
	proposals = dict()
	social_links = None
	alerts = None

	def __init__(self,
				doc=None,
				mongokat_collection=None,
				fetched_fields=None,
				gen_skel=False,
				board_contract=None,
				rules_contract=None,
				token_contract=None,
				registry_contract=None,
				owner=None):
		"""
		doc : dict containing the data to be initialized from
		mongokat_collection : see mongokat.Document (mongo collection associated with the doc)
		fetched_fileds : see mongokat.Document
		gen_skel : boolean. If set to true, the document is initialized with the fields described in OrgaCollection.structure
		board_contract : string containing the name of the orga contract (stored in app/contracts/, .sol must be absent)
		rules : string containing the name of the rules contract
		owner : either an address or a UserDoc, set at creation only
		This constructor function is called in different context :
		At the creation of an organization, the '*_contract' arguments are specified, evm code is compiled and stored into a new ContractDocument
		At the initialization of an existing orga, if the contract id is specified in the document then build a Contract object to interact with it
		An owner can be specified, it will then be used by default for deploying the contract
		"""
		super().__init__(doc=doc, mongokat_collection=organizations, fetched_fields=fetched_fields, gen_skel=gen_skel)
		if board_contract and rules_contract:
			if token_contract:
				self.token = Contract(token_contract, owner.get('account'))
				self.token.compile()
			if registry_contract:
				self.registry = Contract(registry_contract, owner.get('account'))
				self.registry.compile()
			self.rules = Contract(rules_contract, owner.get('account'))
			self.rules.compile()
			self.board = Contract(board_contract, owner.get('account'))
			self.board.compile()

			self.default_rules.update(self["rules"])
			self["rules"] = self.default_rules

			self.default_rights.update(self["rights"])
			self["rights"] = self.default_rights

		elif self.get("contracts"):
			self._loadContracts()
		if owner:
			self["owner"] = (owner.anonymous() if self.get('rules').get("anonymous") else owner.public()) if isinstance(owner, User) else owner


	####
	# CONTRACT SPECIFIC METHODS
	####

	def _loadContracts(self):
		"""
		Build a ContractDocument object to use its methods and interact with the smart contract via its interface
		Update the balance of the contract
		"""

		try:
			self.board = contracts.find_one({"_id": self.get('contracts').get('board').get('_id')})
			balance = self.getTotalFunds()
			if balance != self["balance"]:
				self["balance"] = balance
				self.save_partial()
		except: pass

		try: self.rules = contracts.find_one({"_id": self.get('contracts').get('rules').get('_id')})
		except: pass

		try: self.registry = contracts.find_one({"_id": self.get('contracts').get('registry').get('_id')})
		except: pass

		try: self.token = contracts.find_one({"_id": self.get('contracts').get('token').get('_id')})
		except: pass

	def deployContract(self, from_=None, password=None, args=[]):
		"""
		from_ : address of the account used to deploy the contract (self["owner"] is used by default) 
		password : password to unlock the account
		args : list of arguments to be passed upon the contract creation
		Deploy the contract on the blockchain
		"""
		if from_ is None:
			from_ = self["owner"]

		if not from_.unlockAccount(password=password):
			return "Failed to unlock account"

		try:
			tx_hash = self.token.deploy(from_.get('account'), args=[])
			bw.waitTx(tx_hash)
			token_contract_address = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
			self.token["address"] = token_contract_address
			self.token["is_deployed"] = True
			print("Token is mined !", token_contract_address)
		except AttributeError:
			pass
		try:
			tx_hash = self.registry.deploy(from_.get('account'), args=[])
			bw.waitTx(tx_hash)
			registry_contract_address = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
			self.registry["address"] = registry_contract_address
			self.registry["is_deployed"] = True
			print("Registry is mined !", registry_contract_address)
		except AttributeError:
			pass

		tx_hash = self.rules.deploy(from_.get('account'), args=[])
		bw.waitTx(tx_hash)
		print("Rules are mined !", eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress'))
		self.rules["address"] = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
		self.rules["is_deployed"] = True
		args.append(self.rules["address"])
		tx_hash = self.board.deploy(from_.get('account'), args=args)
		bw.pushEvent(ContractCreationEvent(tx_hash=tx_hash, callbacks=self.register, users=from_))
		return tx_hash


	####
	# CALLBACKS FOR UPDATE
	####

	def register(self, tx_receipt):
		"""
		tx_receipt : dict containing the receipt of the contract creation transaction
		Callback called after a ContractCreationEvent happened : the address, balance, rules and id of the newly created contract are saved in mongo
		The organisation document is returned
		"""
		self.board["address"] = tx_receipt.get('contractAddress')
		self["address"] = tx_receipt.get('contractAddress')
		self.board["is_deployed"] = True
		self["balance"] = self.getTotalFunds()

		self["contracts"] = dict()
		for contract_type, contract_instance in zip(["board", "rules", "registry", "token"], filter(lambda x: x != None, [self.board, self.rules, self.registry, self.token])):
			self["contracts"][contract_type] = {
					"address": contract_instance["address"],
					"_id": contract_instance.save()
				}

		self.save()

		for item in self.get('invited_users'):
			print("ITERATE ON INVITED USERS")
			notification.pushNotif({
				"sender": {"id": objectid.ObjectId(self.get("_id")), "type":"organization"},
				"subject": {"id": objectid.ObjectId(item), "type":"user"},
				"category": "newInviteJoinOrga"
			})



		resp = {"name": self["name"], "_id": str(self["_id"])}
		resp.update({"data" :{k: str(v) if type(v) == ObjectId else v for (k, v) in self.items()}})
		notification.pushNotif({"sender": {"id": objectid.ObjectId(resp.get("data").get("owner").get("_id")), "type": "user"}, "subject": {"id": objectid.ObjectId(resp.get("data").get("_id")), "type": "orga"}, "category": "orgaCreate"})
		return resp

	def memberJoined(self, logs):
		"""
		logs : list of dict containing the event's logs
		If the transaction has succeeded and that the member isn't already part of the members, a new Member is created and stored in the orga document with its rights assigned
		The organisation is returned alongside the rights of the new member
		"""
		if len(logs) == 1 and len(logs[0].get('topics')) == 2 and len(logs[0]["decoded_data"]) == 1:
			address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			new_member = users.find_one({"account": address})
			if new_member and new_member.get('account') not in self.get('members'):
				rights_tag = logs[0]["decoded_data"][0]
				if rights_tag in self.get('rights').keys():
					member_data = new_member.anonymous() if self.get('rules').get("anonymous") else new_member.public()
					public_member =  Member(member_data, rights=self.get('rights').get(rights_tag), tag=rights_tag)
					self["members"][new_member.get('account')] = public_member
					self.save_partial();
					return { "orga": self.public(public_members=True), "rights": public_member.get('rights')}

		return False

	def memberLeft(self, logs):
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

	def newDonation(self, logs):
		"""
		logs : list of dict containing the event's logs
		If the transaction has succeeded, add the amount of the donation to the member's data
		"""
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
		"""
		logs : list of dict containing the event's logs
		If the transaction has succeeded, create a new ProjectDocument and save its data into the orga document
		"""
		if len(logs) == 1 and len(logs[0].get('topics')) == 2:
			contract_address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			new_project = ProjectDocument(at=contract_address, contract='basic_project', owner=self.public())
			if len(logs[0]["decoded_data"]) == 1:
				new_project["name"] = logs[0]["decoded_data"][0]
			project_id = new_project.save()
			if contract_address not in self["projects"]:
				self["projects"][contract_address] = new_project
				self.save_partial()
				return self
		return False

	def offerCreated(self, logs):
		"""
		logs : list of dict containing the event's logs
		If the transaction has succeeded, create a new ProjectDocument and save its data into the orga document
		"""
		if len(logs) == 1 and len(logs[0].get('topics')) == 3:
			offer_address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
			contractor = normalizeAddress(logs[0].get('topics')[2], hexa=True)
			new_offer = Offer(at=offer_address, contract='Offer', owner=contractor)
			new_offer.contract["is_deployed"] = True
			new_offer.initFromContract()
			new_offer["contract_id"] = new_offer.contract.save()
			if offer_address not in self["offers"]:
				self["offers"][offer_address] = new_offer
				self.save_partial()
				return self
		return False

	def proposalCreated(self, logs):
		"""
		logs : list of dict containing the event's logs
		If the transaction has succeeded, create a new ProjectDocument and save its data into the orga document
		"""
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
		"""
		user : userDoc
		action : string describing the action (see self.get('rights'). eg : "create_project")
		Chef if 'user' has permission to execute action 'action'.
		Returns a boolean
		"""
		member = self.getMember(user)
		if member:
			return member.get('rights', {}).get(action)
		else:
			return self.get('rights').get('default').get(action)

	####
	# GENERIC METHODS
	####

	def public(self, additional_infos=None, public_members=False):
		"""
		additional_infos : list of all the fields we want to include in the return value
		public_members : boolean. If set to True, information about the members is returned
		Returns a public version of the document stored in db that can be read by all users
		"""

		to_be_public = organizations.public_info
		if additional_infos:
			to_be_public += additional_infos
		ret = {key: self.get(key) for key in self if key in to_be_public}

		if public_members:
			ret.update({"members":{account: {"name": None if self.get('rules').get("anonymous") else member["name"],
											"_id": member["_id"],
											"account": account,
											"tag": member["tag"]} for account, member in self.get('members').items()}})
		return ret


	def getMember(self, user):
		"""
		user : UserDoc
		Returns the member corresponding to the user passed as param, None if there is no match
		"""
		if isinstance(user, User):
			account = user.get('account')
			if account in self["members"]:
				return self["members"][account]
			else:
				for member in self["members"].values():
					if user.get('_id')  == member.get('_id'):
						return member
		elif type(user) is str and user in self["members"]:
				return self["members"][user]
		return None

	def getTotalFunds(self):
		"""
		Returns the total balance of the contract, in ether
		"""
		return fromWei(self.board.getBalance())

	def getMemberList(self):
		"""
		Returns a list of all members. Only the anonymous data is returned in case the 'anonymous' field has been specified.
		"""
		memberAddressList = ["0x" + member.decode('utf-8') for member in self.board.call("getMemberList")]
		memberList = users.find({"account": {"$in": memberAddressList}}, users.anonymous_info if self.get('rules').get("anonymous") else users.public_info)
		return list(memberList)

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

		tx_hash = self.board.call('join', local=local, from_=user.get('account'), args=[user.get('name'), tag], password=password)
		if tx_hash and tx_hash.startswith('0x'):
			topics = makeTopics(self.board.getAbi("newMember").get('signature'), user.get('account'))
			
			mail = {'sender':self, 'subject':user, 'users':[user], 'category':'newMember'}
			bw.pushEvent(LogEvent("newMember", tx_hash, self.board["address"], topics=topics, callbacks=[self.memberJoined, user.joinedOrga], users=user, event_abi=self.board["abi"], mail=mail))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def leave(self, user, password=None, local=False):
		"""
		user : UserDoc initiating the action
		password : password unlocking the account at the origin of the action
		local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
		Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
		Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
		"""
		if not self.can(user, "leave"):
			return False

		tx_hash = self.board.call('leave', local=local, from_=user.get('account'), password=password)
		if tx_hash and tx_hash.startswith('0x'):
			topics = makeTopics(self.board.getAbi("memberLeft").get('signature'), user.get('account'))
			bw.pushEvent(LogEvent("memberLeft", tx_hash, self.board["address"], topics=topics, callbacks=[self.memberLeft, user.leftOrga], users=user))
			user.needsReloading()
			return tx_hash
		else:
			return False

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
			topics = makeTopics(self.board.getAbi("DonationMade").get('signature'), user.get('account'))
			bw.pushEvent(LogEvent("DonationMade", tx_hash, self.board["address"], topics=topics, callbacks=[user.madeDonation, self.newDonation], users=user))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def kill(self, from_):
		return None

	def createProject(self, user, project, password=None):
		"""
		user : UserDoc initiating the action
		password : password unlocking the account at the origin of the action
		local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
		Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
		Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
		"""
		if not self.can(user, "create_project"):
			return False
		tx_hash = self.board.call('createProject', local=False, from_=user.get('account'), args=[project.get('name', 'newProject')], password=password)

		if tx_hash and tx_hash.startswith('0x'):
			bw.pushEvent(LogEvent("ProjectCreated", tx_hash, self.board["address"], callbacks=[self.projectCreated], users=user, event_abi=self.board["abi"]))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def killProject(self, project):
		return None

	def createOffer(self, user, offer, password=None):
		"""
		check if sender can create offer
		check if offer is valid (client == orga, ...)
		deploy offer contract and set callback
		return tx_hash
		"""
		if not self.can(user, "create_offer"):
			return "unauthorized"
	
		try:
			offer["hashOfTheProposalDocument"] = offer["hashOfTheProposalDocument"].encode('utf-8')[:32]
			args = [offer['contractor'], offer['client'], offer['hashOfTheProposalDocument'], offer['totalCost'], offer['initialWithdrawal'], offer['minDailyWithdrawalLimit'], offer['payoutFreezePeriod'], offer['isRecurrent'], offer['duration']]
		except KeyError:
			return "missing param in %s" % arg
		
		tx_hash = self.board.call('createOffer', local=False, from_=user.get('account'), args=args, password=password)

		if tx_hash and tx_hash.startswith('0x'):
			bw.pushEvent(LogEvent("OfferCreated", tx_hash, self.board["address"], callbacks=[self.offerCreated], users=user, event_abi=self.board["abi"]))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def cancelOffer(self, user, offer, password=None):
		"""
		a user can cancel its own offer
		"""
		tx_hash = self.board.call('cancelOffer', local=False, from_=user.get('account'), args=[offer.get('name', 'newProject')], password=password)

		if tx_hash and tx_hash.startswith('0x'):
			bw.pushEvent(LogEvent("OfferCanceled", tx_hash, self.board["address"], callbacks=[self.projectCreated], users=user, event_abi=self.board["abi"]))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def createProposal(self, user, proposal, password=None):
		"""
		canSenderPropose
		check proposal (_name, _type, , _description, _proxy, _debatePeriod, _destination, _value, _calldata)
		destination is a valid offer from orga
		deploy proposal contract and set callback
		return tx_hash
		"""
		try:
			args = [offer[parameter] for parameter in ['name', 'debatePeriod', 'destination', 'value', 'calldata', 'decription']]
		except KeyError:
			return False

		tx_hash = self.board.call('createProject', local=False, from_=user.get('account'), args=[project.get('name', 'newProject')], password=password)

		if tx_hash and tx_hash.startswith('0x'):
			bw.pushEvent(LogEvent("ProposalCreated", tx_hash, self.board["address"], callbacks=[self.proposalCreated], users=user, event_abi=self.board["abi"]))
			user.needsReloading()
			return tx_hash
		else:
			return False


	def voteForProposal(self, user, proposal, password=None):
		"""
		can sender vote
		send tx and return hash
		"""
		tx_hash = self.board.call('createProject', local=False, from_=user.get('account'), args=[project.get('name', 'newProject')], password=password)

		if tx_hash and tx_hash.startswith('0x'):
			bw.pushEvent(LogEvent("newProject", tx_hash, self.board["address"], callbacks=[self.projectCreated], users=user, event_abi=self.board["abi"]))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def executeProposal(self, user, proposal, password=None):
		"""
		if proposal is finished and not executed
		sen tx and return hash
		"""
		tx_hash = self.board.call('createProject', local=False, from_=user.get('account'), args=[project.get('name', 'newProject')], password=password)

		if tx_hash and tx_hash.startswith('0x'):
			bw.pushEvent(LogEvent("newProject", tx_hash, self.board["address"], callbacks=[self.projectCreated], users=user, event_abi=self.board["abi"]))
			user.needsReloading()
			return tx_hash
		else:
			return False

	def changeConstitution(self, user, constitution):
		"""
		deploy new Rules contract and call changeRules with the address of the new contract
		"""
		return None


class OrgaCollection(Collection):
	"""
	Abstraction of the 'organizations' mongo collection
	Overrides a mongokat.Collection
	"""

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
		"offers": dict,
		"proposals": dict,
		"projects": dict,
		"description": str,
		"owner": dict,
		"contracts": dict,
		"files": dict,
		"tx_history": list,
		"creation_date": str,
		"mailing_lists": dict,
		"accounting_data": str,
		"alerts": list,
		"social_accounts": dict,
		"balance": int,
		"uploaded_documents": list,
		"gov_model": str,
		"invited_users": list
	}

	def lookup(self, query):
		"""
		query : either a string or a regex
		Look for a name matching 'query'
		Returns the list of the results. Each result is tagged with a flag {"category": "organization"}
		"""
		results = list(super().find({"name": query, "hidden": False}, ["_id", "name", "address"]))
		for doc in results:
			doc.update({"category": "organization"})
		return results

	@find_method
	def find_one(self, *args, **kwargs):
		"""
		args : see mongokat.Collection.find_one
		kwargs : see mongokat.Collection.find_one
		Overload the parent find_one function to initialize the Contract object which has its _id contained in the orga document
		"""
		from .orga_models import governances
		
		doc = super().find_one(*args, **kwargs)
		doc = governances[doc["gov_model"]]["templateClass"](doc)
		doc.__init__()
		return doc

organizations = OrgaCollection(collection=client.main.organizations)

