proposal_status = [
"pending",
"debating",
"denied",
"approved"
]

class Proposal(dict):
	
	structure = {
	"name": str,
	"executed": bool,
	"participation": int,
	"offer": dict,
	"time_left": int,
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
			self["executed"] = board.call("isExecuted", args=[proposal_id], local=True)
			self["destination"] = board.call("destinationOf", args=[proposal_id], local=True)
			self["value"] = str(board.call("valueOf", args=[proposal_id], local=True))
			self["hashed_calldata"] = board.call("hashOf", args=[proposal_id], local=True)
			self["debate_period"] = board.call("debatePeriodOf", args=[proposal_id], local=True)
			self["created_on"] = board.call("createdOn", args=[proposal_id], local=True)
			self["from"] = board.call("createdBy", args=[proposal_id], local=True)