from models import contract

offer_types = [
"employment",
"investment",
"service",
"tax",
]

class Offer(contract.ContractDocument):

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
			self["contractor"] = owner or '0x' + self.call('getContractor', local=True)
			self["client"] = '0x' + self.call('getClient', local=True)
			self["creationDate"] = self.call('getCreationDate', local=True)
			self["hashOfTheProposalDocument"] = self.call('getHashOfTheProposalDocument', local=True)
			self["initialWithdrawal"] = str(self.call('getInitialWithdrawal', local=True))
			self["dailyWithdrawalLimit"] = str(self.call('getDailyWithdrawalLimit', local=True))
			self["payoutFreezePeriod"] = self.call('getPayoutFreezePeriod', local=True)
			self["isRecurrent"] = self.call('getIsRecurrent', local=True)
			self["duration"] = self.call('getDuration', local=True)
			self["type"] = self.call('getOfferType', local=True)
