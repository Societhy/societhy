from mongokat import Collection, Document
from .clients import client

class ProjectDocument(Document):

	contract  None
	owner = None
	members = None
	description = None
	goals = None
	balance = None
	proposals = list()
	campaigns = None
	files = None

	def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None):
		super().__init__(doc, projects, fetched_fields, gen_skel)

	def getMemberList(self):
		pass

	def join(self, user):
		pass

	def leave(self, member):
		pass

	def kill(self, from_):
		pass

	def donate(self, from_):
		pass

	def createCampaign(self, campaign, from_):
		pass

	def endCampaign(self, campaign):
		pass

	def createProposal(self, proposal):
		pass

	def killProposal(self, proposal):
		pass

	def transferOwnership(self, from_, to_):
		pass

class ProjectCollection(Collection):
	pass

projects = ProjectCollection(collection=client.main.projects)