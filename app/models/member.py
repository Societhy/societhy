from models import user


class Tag:
    pass


class Member(user.UserDocument):
    organization = None
    rights = None

    def __init__(self, user, tag=None):
        if tag:
            user["tag"] = tag
        self["votes"] = list()
        super().__init__(doc=user, gen_skel=False)

    def saveVotes(self, destination, vote):
        self["votes"].append({"offer": destination, "vote": vote})
        self.save_partial()

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
