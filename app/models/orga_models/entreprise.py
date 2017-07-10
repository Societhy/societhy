from ..organization import OrgaDocument as Organization
import models.notification
from bson import objectid
import datetime
from models.user import users, UserDocument as User

class Entreprise(Organization):

	default_rules = {
		"default_proposal_duration": 1,
		"payout_freeze_period": 0,
		"delegated_voting": False,
		"quorum": 20,
		"majority": 50,
		"accessibility": "private",
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
			"publish_news": True,
            "edit_rights": True,
            "edit_jobs": True,
            "access_administration": True
		},
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
            "edit_rights": True,
            "edit_jobs": True,
            "access_administration": True
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
            "edit_rights": False,
            "edit_jobs": False,
            "access_administration": False
		}
	}

	def register(self, tx_receipt, callback_data=None):
		"""
		tx_receipt : dict containing the receipt of the contract creation transaction
		Callback called after a ContractCreationEvent happened : the address, balance, rules and id of the newly created contract are saved in mongo
		The organisation document is returned
		"""
		self.board["address"] = tx_receipt.get('contractAddress')
		self["address"] = tx_receipt.get('contractAddress')
		self.board["is_deployed"] = True

		#ADD OWNER
		from_ = callback_data.get('from')
		from_.unlockAccount(password=callback_data.get('password'))
		tx_hash = self.join(from_, tag="owner", password=callback_data.get('password'), local=False)
		if not tx_hash:
			return {"data": "User does not have permission to join", "status": 400}

		#SEND FUNDS TO ORGA AFTER IT IS CREATED
		if callback_data and callback_data.get('action') == "donate" and callback_data.get("initial_funds", 0) > 0:
			amount = float(callback_data.get('initial_funds'))
			if from_.refreshBalance() > amount:
				from_.session_token = None
				from_.unlockAccount(password=callback_data.get('password'))
				tx_hash = self.donate(from_, toWei(amount), password=callback_data.get('password'), local=False)
				if not tx_hash:
					return {"data": "User does not have permission to donate", "status": 400}
			else:
				return {"data": "Not enough funds in your wallet to process donation", "status": 400}


		self["balance"] = self.getTotalFunds()

		self["contracts"] = dict()
		for contract_type, contract_instance in {k:v for k,v in {"board": self.board, "rules": self.rules, "registry": self.registry, "token": self.token, 'token_freezer': self.token_freezer}.items() if v is not None}.items():
			self["contracts"][contract_type] = {
					"address": contract_instance["address"],
					"_id": contract_instance.save()
				}
		self.save()

		for item in self.get('invited_users'):
			notif = models.notification.NotificationDocument({
				"sender": {"id": objectid.ObjectId(self.get("_id")), "type":"organization"},
				"subject": {"id": objectid.ObjectId(item), "type":"user"},
				"category": "newInviteJoinOrga",
				"angularState": {
					"route":"app.organization",
					"params":{
						"_id":str(self.get("_id")),
						"name":self.get("name")
					}
				},
				"description": "You have been invited in the organisation " + self["name"] + " by " + callback_data.get('from')["name"]  + " as a " + self.get("invited_users").get(item)["tag"]
			})
			notif.save()
			user = users.find_one({"_id":objectid.ObjectId(item)})
			user.get("pending_invitation").append({"type":"organisation", "id":str(self.get("_id"))})
			from_.unlockAccount(password=callback_data.get('password'))
			self.allow(from_, user.get('account'), None, password=callback_data.get('password'), local=False)
			user.save()

		resp = {"name": self["name"], "_id": str(self["_id"])}
		resp.update({"data" :{k: str(v) if type(v) == objectid.ObjectId else v for (k, v) in self.items()}})
		notif = models.notification.NotificationDocument({
			"sender": {"id": objectid.ObjectId(resp.get("data").get("_id")), "type": "orga"},
			"subject": {"id": objectid.ObjectId(resp.get("data").get("owner").get("_id")), "type": "user"},
			"category": "orgaCreated",
			"angularState": {
				"route":"app.organization",
				"params":{
					"_id":str(self.get("_id")),
						"name":self.get("name")
				}
                        },
                        "description": "The organization " + self["name"] + "was created by " +  callback_data.get('from')["name"] + ".", 
                        "createdAt": datetime.datetime.now(),
                        "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")})
		notif.save()
		return resp

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

	def transferOwnership(self, from_, to_):
		return None
