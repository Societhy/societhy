from mongokat import Collection, Document

from ..clients import client, eth_cli
from ..organization import OrgaDocument as Organization

from models.events import Event, ContractCreationEvent, LogEvent, makeTopics
from models.user import users, UserDocument as User
from models.contract import contracts, ContractDocument as Contract
from models.project import ProjectDocument, ProjectCollection
from models.member import Member
from models.notification import NotificationDocument as Notification, notifications as notification
from models.offer import Offer
from models.proposal import Proposal

from core.utils import fromWei, toWei, to20bytes, to32bytes, normalizeAddress
from core.blockchain_watcher import blockchain_watcher as bw

class PublicCompany(Organization):

	default_rules = {
		"default_proposal_duration": 1,
		"payout_freeze_period": 0,
		"delegated_voting": False,
		"quorum": 20,
		"majority": 50,
		"accessibility": "open",
		"can_be_removed": True,
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
			"create_project": True,
			"create_offer": True,
			"create_proposal": True,
			"vote_proposal": True,
			"recruit": True,
			"remove_members": True,
			"sell_token": True,
			"buy_token": True,
		},
		"admin": {},
		"partner": {},
		"member": {
			"join": False,
			"leave": True,
			"donate": True,
			"create_project": False,
			"create_offer": True,
			"create_proposal": False,
			"vote_proposal": True,
			"recruit": False,
			"remove_members": False,
			"sell_token": True,
			"buy_token": True,
		},
		"default": {
			"join": True,
			"leave": False,
			"donate": True,
			"create_project": False,
			"create_offer": True,
			"create_proposal": False,
			"vote_proposal": False,
			"recruit": False,
			"remove_members": False,
			"sell_token": False,
			"buy_token": False,
		}
	}

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
			from_.unlockAccount(password=password)
			tx_hash = self.token.deploy(from_.get('account'), args=[])
			bw.waitTx(tx_hash)
			token_contract_address = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
			self.token["address"] = token_contract_address
			self.token["is_deployed"] = True
			print("Token is mined !", token_contract_address)
			from_.unlockAccount(password=password)
			tx_hash = self.token_freezer.deploy(from_.get('account'), args=[self.token["address"]])
			bw.waitTx(tx_hash)
			token_freezer_contract_address = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
			self.token_freezer["address"] = token_freezer_contract_address
			self.token_freezer["is_deployed"] = True
			print("Token Freezer is mined !", token_contract_address)
		except AttributeError:
			pass

		from_.unlockAccount(password=password)
		tx_hash = self.rules.deploy(from_.get('account'), args=[self.token_freezer["address"], list(), 0])
		bw.waitTx(tx_hash)
		print("Rules are mined !", eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress'))
		self.rules["address"] = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
		self.rules["is_deployed"] = True
		args.append(self.rules["address"])
		args.append(0)
		from_.unlockAccount(password=password)
		tx_hash = self.board.deploy(from_.get('account'), args=args)

		action = {
			"action": "donate",
			"from": from_,
			"password": password,
			"initial_funds": self.get('initial_funds')
			} if self.get('initial_funds', 0) > 0 else None

		bw.pushEvent(ContractCreationEvent(tx_hash=tx_hash, callbacks=self.register, callback_data=action, users=from_))
		return tx_hash	


	def launchCrowdfunding(self, params):
		pass

	def addLegalDocument(self, document):
		pass

	def setScheduledPayment(self, payment, to_):
		pass

	def hireEmployee(self, employee, params):
		pass

	def createPartnership(self, with_, params):
		pass

	def sellShare(self, selling, to_):
		pass

	def computeStatistics(self, data, params):
		pass