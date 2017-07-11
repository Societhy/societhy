from ..organization import OrgaDocument as Organization

class Ngo(Organization):

	default_rules = {
		"default_proposal_duration": 120,
		"payout_freeze_period": 0,
		"delegated_voting": False,
		"quorum": 20,
		"majority": 50,
		"accessibility": "public",
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
			"create_proposal": False,
			"create_offer": True,
			"vote_proposal": True,
			"recruit": False,
			"remove_members": False,
			"sell_token": True,
			"buy_token": True,
			"publish_news": True,
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
			"publish_news": True,
            "edit_rights": False,
            "edit_jobs": False,
            "access_administration": False
		}
	}
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