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

proposal_types = [
"employment",
"investment",
"service",
"tax",
]

tmp = {
"0xdeadbeefdeadbeef": {
	"name": "first",
	"participation": 50,
	"beneficiary": "Joseph Martin",
	"from": "0xab1393Njdjdndn8820dlnjncmc",
	"status": "denied",
	"votes_count": 176,
	"created_on": "May 03, 2017 11:42 AM"
	},
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
	
	name = str()
	debatePeriod = 0
	destination = None
	beneficiary = None
	value = 0
	_calldata = None
	status = None

	def __init__(self, board, proposal_id):

		self[""] = self.board.call("", args=[proposal_id], local=True)