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

class Offer(Contract):

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
		super().__init__(doc=doc, contract=contract, owner=owner)
		if at:
			self["address"] = at
			self.compile()

	def initFromContract(self):
		if self.get("address") and self.get("is_deployed"):
			self["contractor"] = '0x' + self.call('getContractor', local=True)
			self["client"] = '0x' + self.call('getClient', local=True)
			self["creationDate"] = self.call('getCreationDate', local=True)
			self["hashOfTheProposalDocument"] = self.call('getHashOfTheProposalDocument', local=True)
			self["totalCost"] = self.call('getTotalCost', local=True)
			self["initialWithdrawal"] = self.call('getInitialWithdrawal', local=True)
			self["minDailyWithdrawalLimit"] = self.call('getMinDailyWithdrawalLimit', local=True)
			self["payoutFreezePeriod"] = self.call('getPayoutFreezePeriod', local=True)
			self["isRecurrent"] = self.call('getIsRecurrent', local=True)
			self["duration"] = self.call('getDuration', local=True)
