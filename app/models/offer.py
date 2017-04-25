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

from core.blockchain_watcher import blockchain_watcher as bw
from core.utils import fromWei, toWei, to20bytes, to32bytes, normalizeAddress

from .clients import client, eth_cli

class Offer(dict):

	address = None
	contract_id = None
	creation_date = None
	client = None
	contractor = None
	hashOfTheProposalDocument = None
	totalCost = None
	initialWithdrawal = None
	minDailyWithdrawalLimit = None
	payoutFreezePeriod = None
	isRecurrent = None
	duration = None

	def __init__(self, at=None, contract=None, owner=None, doc={}):
		super().__init__(doc)
		if contract:
			self.contract = Contract(contract, owner)
			self.contract.compile()
			if at:
				self["address"] = at
				self.contract["address"] = at
				
		elif self.get("contract_id"):
			self._loadContracts()
		if owner:
			self["owner"] = owner.public() if issubclass(type(owner), Document) else owner

	def initFromContract(self):
		if self.get("address") and self.contract.get("is_deployed"):
			self["client"] = self.contract.call('getClient', local=True)
			self["creationDate"] = self.contract.call('getCreationDate', local=True)
			self["hashOfTheProposalDocument"] = self.contract.call('getHashOfTheProposalDocument', local=True)
			self["totalCost"] = self.contract.call('getTotalCost', local=True)
			self["initialWithdrawal"] = self.contract.call('getInitialWithdrawal', local=True)
			self["minDailyWithdrawalLimit"] = self.contract.call('getMinDailyWithdrawalLimit', local=True)
			self["payoutFreezePeriod"] = self.contract.call('getPayoutFreezePeriod', local=True)
			self["isRecurrent"] = self.contract.call('getIsRecurrent', local=True)
			self["duration"] = self.contract.call('getDuration', local=True)
			print("-------------------", self)
