from .user import users, UserDocument as User
from ethjsonrpc import wei_to_ether

class Tag:
	pass

class Member(User):

	organization = None
	rights = None

	def __init__(self, user, rights=None, tag=None):
		if rights:
			user.update({"rights": rights})
		if tag:
			user["tag"] = tag
		self["votes"] = list()
		super().__init__(doc=user, gen_skel=False)

	def saveVotes(self, destination, vote):
		user = users.find_one({"_id": self["_id"]})
		user["votes"].append({"offer": destination, "vote": vote})
		user.save_partial()
		self["votes"].append({"offer": destination, "vote": vote})

	def canDo(self, action):
		pass

	def initFromRights(self, rights):
		if isinstance(rights, dict):
			pass
		elif isinstance(rights, Tag):
			pass
		return None

	def setRight(self, action, right):
		pass

	def setRightFromTag(self, action, tag):
		pass