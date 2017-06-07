from bson import ObjectId, Int64

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

offer_types = [
"employment",
"investment",
"service",
"tax",
]

class Offer(Contract):

	address = None
	contract = None
	contract_id = None
	creation_date = None
	description = None
	client = None
	contractor = None
	hashOfTheProposalDocument = None
	initialWithdrawal = None
	minDailyWithdrawalLimit = None
	payoutFreezePeriod = None
	isRecurrent = None
	duration = None
	actors = None
	type = None

	def __init__(self, at=None, contract=None, owner=None, doc={}, init_from_contract=False):
		super().__init__(doc=doc, contract=contract, owner=owner)
		if at:
			self["address"] = at
			self.compile()
		if init_from_contract and self.get("address"):
			self["contractor"] = '0x' + self.call('getContractor', local=True).decode()
			self["client"] = '0x' + self.call('getClient', local=True).decode()
			self["creationDate"] = self.call('getCreationDate', local=True)
			self["hashOfTheProposalDocument"] = self.call('getHashOfTheProposalDocument', local=True)
			self["initialWithdrawal"] = str(self.call('getInitialWithdrawal', local=True))
			self["dailyWithdrawalLimit"] = str(self.call('getDailyWithdrawalLimit', local=True))
			self["payoutFreezePeriod"] = self.call('getPayoutFreezePeriod', local=True)
			self["isRecurrent"] = self.call('getIsRecurrent', local=True)
			self["duration"] = self.call('getDuration', local=True)
			self["type"] = self.call('getOfferType', local=True)
