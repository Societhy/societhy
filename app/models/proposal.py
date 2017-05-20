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

proposal_status = [
"pending",
"debating",
"success",
"approved"
]

tmp = {
"0xdeadbeefdeadofff": {
	"name": "second",
	"participation": 90,
	"beneficiary": "Mireille Schultz",
	"from": "0xb8ml9jgv5chj5",
	"status": "approved",
	"votes_count": 801,
	"created_on": "May 04, 2014 11:52 AM"
	}
}
proposal_status = []

class Proposal(dict):
	
	structure = {
	"name": str,
	"participation": int,
	"offer": dict,
	"debate_period": int,
	"destination": str,
	"value": int,
	"_calldata": bytes,
	"status": str,
	"votes_count": int,
	"created_on": str,
	"from": str,
	"id": int
}
	def __init__(self, doc={}, board=None, init_from_contract=False):
		self.update(doc)
		proposal_id = self.get('proposal_id')
		if init_from_contract and board and proposal_id is not None: 
			self["destination"] = '0x' + board.call("destinationOf", args=[proposal_id], local=True)
			self["value"] = board.call("valueOf", args=[proposal_id], local=True)
			self["hashed_calldata"] = '0x' + board.call("hashOf", args=[proposal_id], local=True)
			self["debate_period"] = board.call("debatePeriodOf", args=[proposal_id], local=True)
			self["created_on"] = board.call("createdOn", args=[proposal_id], local=True)
			self["from"] = '0x' + board.call("createdBy", args=[proposal_id], local=True)
