import datetime
from hashlib import sha3_256

import models.contract
import models.member
import models.notification
from bson import ObjectId
from bson import objectid
from core.utils import fromWei, toWei, normalizeAddress
from models.clients import blockchain_watcher as bw
from models.events import ContractCreationEvent, LogEvent, makeTopics
from models.notification import notifications, NotificationDocument as Notification
from models.offer import Offer
from models.project import ProjectDocument
from models.proposal import Proposal
from models.user import users, UserDocument as User
from mongokat import Collection, Document, find_method

from .clients import client, eth_cli

"""
This module implements the organization class alongside with all its methods
"""

class OrganisationInitializationError(Exception):
    pass

class OrgaDocument(Document):
    """
    Overrides a mongokat.Document and add custom methods
    This class is used everytime a controller needs to manipulate an organisation
    """

    board = None
    rules = None
    registry = None
    token = None
    token_freezer = None
    members = dict()
    files = dict()
    projects = dict()
    proposals = dict()
    social_links = None
    alerts = None
    transactions = dict()
    default_weight = {
        "owner": 3,
        "partner": 2,
        "admin": 2,
        "member": 1,
        "default": 0
    }
    def __init__(self,
                doc=None,
                mongokat_collection=None,
                fetched_fields=None,
                gen_skel=False,
                board_contract=None,
                rules_contract=None,
                token_contract=None,
                token_freezer_contract=None,
                registry_contract=None,
                owner=None):
        """
        doc : dict containing the data to be initialized from
        mongokat_collection : see mongokat.Document (mongo collection associated with the doc)
        fetched_fileds : see mongokat.Document
        gen_skel : boolean. If set to true, the document is initialized with the fields described in OrgaCollection.structure
        board_contract : string containing the name of the orga contract (stored in app/contracts/, .sol must be absent)
        rules : string containing the name of the rules contract
        owner : either an address or a UserDoc, set at creation only
        This constructor function is called in different context :
        At the creation of an organization, the '*_contract' arguments are specified, evm code is compiled and stored into a new ContractDocument
        At the initialization of an existing orga, if the contract id is specified in the document then build a Contract object to interact with it
        An owner can be specified, it will then be used by default for deploying the contract
        """
        super().__init__(doc=doc, mongokat_collection=organizations, fetched_fields=fetched_fields, gen_skel=gen_skel)
        if board_contract and rules_contract:
            if token_contract:
                self.token = models.contract.ContractDocument(token_contract, owner.get('account'))
                self.token.compile()
                if token_freezer_contract:
                    self.token_freezer = models.contract.ContractDocument(token_freezer_contract, owner.get('account'))
                    self.token_freezer.compile()
            if registry_contract:
                self.registry = models.contract.ContractDocument(registry_contract, owner.get('account'))
                self.registry.compile()
            self.rules = models.contract.ContractDocument(rules_contract, owner.get('account'))
            self.rules.compile()
            self.board = models.contract.ContractDocument(board_contract, owner.get('account'))
            self.board.compile()

            self.default_rules.update(self["rules"])
            self["rules"] = self.default_rules

            for role, rights in self["rights"].items():
                rights['weight'] = self.default_weight.get(role, 1)
            self.default_rights.update(self["rights"])
            self["rights"] = self.default_rights

        elif self.get("contracts"):
            self._loadContracts()
        if owner:
            self["owner"] = (owner.anonymous() if self.get('rules').get("anonymous") else owner.public()) if isinstance(owner, User) else owner

    ####
    # CONTRACT SPECIFIC METHODS: _loadContracts, deployContract, register
    ####

    def _loadContracts(self):
        """
        Build a ContractDocument object to use its methods and interact with the smart contract via its interface
        Update the balance of the contract
        """

        try:
            self.board = models.contract.contracts.find_one({"_id": self.get('contracts').get('board').get('_id')})
            balance = self.getTotalFunds()
            if balance != self["balance"]:
                self["balance"] = balance
                self.save_partial()
        except: pass

        try: self.rules = models.contract.contracts.find_one({"_id": self.get('contracts').get('rules').get('_id')})
        except: pass

        try: self.registry = models.contract.contracts.find_one({"_id": self.get('contracts').get('registry').get('_id')})
        except: pass

        try: self.token = models.contract.contracts.find_one({"_id": self.get('contracts').get('token').get('_id')})
        except: pass

        try: self.token_freezer = models.contract.contracts.find_one({"_id": self.get('contracts').get('token_freezer').get('_id')})
        except: pass

    def deployContract(self, from_=None, password=None, args=[]):
        """
        from_ : address of the account used to deploy the contract (self["owner"] is used by default)
        password : password to unlock the account
        args : list of arguments to be passed upon the contract creation
        Deploy the contract on the blockchain
        """
        if from_ is None:
            from_ = self["owner"]

        if not from_.unlockAccount(password=password):
            return "Failed to unlock account"

        try:
            from_.unlockAccount(password=password)
            tx_hash = self.token.deploy(from_.get('account'), args=[])
            bw.waitTx(tx_hash)
            token_contract_address = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
            self.token["address"] = token_contract_address
            self.token["is_deployed"] = True
            print("Token is mined !", token_contract_address)
        except AttributeError:
            pass

        try:
            from_.unlockAccount(password=password)
            tx_hash = self.token_freezer.deploy(from_.get('account'), args=[self.token["address"]])
            bw.waitTx(tx_hash)
            token_freezer_contract_address = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
            self.token_freezer["address"] = token_freezer_contract_address
            self.token_freezer["is_deployed"] = True
            print("Token Freezer is mined !", token_freezer_contract_address)
        except AttributeError:
            pass

        try:
            from_.unlockAccount(password=password)
            tx_hash = self.registry.deploy(from_.get('account'), args=[])
            bw.waitTx(tx_hash)
            registry_contract_address = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
            self.registry["address"] = registry_contract_address
            self.registry["is_deployed"] = True
            print("Registry is mined !", registry_contract_address)
        except AttributeError:
            pass
        from_.unlockAccount(password=password)
        tx_hash = self.rules.deploy(from_.get('account'), args=[self.registry["address"]])
        bw.waitTx(tx_hash)
        print("Rules are mined !", eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress'))
        self.rules["address"] = eth_cli.eth_getTransactionReceipt(tx_hash).get('contractAddress')
        self.rules["is_deployed"] = True
        args.append(self.rules["address"])
        args.append(self.registry["address"])
        from_.unlockAccount(password=password)
        tx_hash = self.board.deploy(from_.get('account'), args=args)

        action = {
            "action": "donate",
            "from": from_,
            "password": password,
            "initial_funds": self.get('initial_funds', 0)
            }

        bw.pushEvent(ContractCreationEvent(tx_hash=tx_hash, callbacks=self.register, callback_data=action, users=from_))
        return tx_hash

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
            print(item)
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
            user.save()

        resp = {"name": self["name"], "_id": str(self["_id"])}
        resp.update({"data" :{k: str(v) if type(v) == ObjectId else v for (k, v) in self.items()}})
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

    ####
    # RIGHTS MANAGEMENT: setRights, can
    ####

    def setRights(self, user, actions, rights):
        pass

    def can(self, user, action):
        """
        user : userDoc
        action : string describing the action (see self.get('rights'). eg : "create_project")
        Chef if 'user' has permission to execute action 'action'.
        Returns a boolean
        """
        member = self.getMember(user)
        if member:
            return self.get('rights').get(member.get('tag')).get(action)
        else:
            return self.get('rights').get('default').get(action)

    ####
    # GENERIC METHODS : public, getMember, getTotalFunds, getMemberList
    ####

    def public(self, additional_infos=None, public_members=False):
        """
        additional_infos : list of all the fields we want to include in the return value
        public_members : boolean. If set to True, information about the members is returned
        Returns a public version of the document stored in db that can be read by all users
        """

        to_be_public = organizations.public_info
        if additional_infos:
            to_be_public += additional_infos
        ret = {key: self.get(key) for key in self if key in to_be_public}

        if public_members:
            ret.update({"members":{account: {"name": None if self.get('rules').get("anonymous") else member["name"],
                                            "_id": member["_id"],
                                            "account": account,
                                            "tag": member["tag"]} for account, member in self.get('members').items()}})
        return ret


    def getMember(self, user):
        """
        user : UserDoc
        Returns the member corresponding to the user passed as param, None if there is no match
        """
        if isinstance(user, User):
            account = user.get('account')
            if account in self["members"]:
                return models.member.Member(self["members"][account])
            else:
                for member in self["members"].values():
                    if user.get('_id')  == member.get('_id'):
                        return models.member.Member(member)
        elif type(user) is str and user in self["members"]:
                return models.member.Member(self["members"][user])
        return None

    def getTotalFunds(self):
        """
        Returns the total balance of the contract, in ether
        """
        return fromWei(self.board.getBalance())

    def getMemberList(self):
        """
        Returns a list of all members. Only the anonymous data is returned in case the 'anonymous' field has been specified.
        """
        memberList = list(users.find({"account": {"$in": self.registry.call("getMemberList")}}, users.anonymous_info if self.get('rules').get("anonymous") else users.public_info))
        return memberList

    def inviteUsers(self, user, invited_users):
        for key, item in invited_users.items():
            self['invited_users'][key] = item
            self.save_partial()
            notif = models.notification.NotificationDocument({
                "sender": {"id": objectid.ObjectId(self.get("_id")), "type": "organization"},
                "subject": {"id": objectid.ObjectId(key), "type": "user"},
                "category": "newInviteJoinOrga",
                "angularState": {
                    "route":"app.organization",
                    "params":{
                        "_id":str(self.get("_id")),
                        "name":self.get("name")
                    }
                },
                "description": "You have been invited in the organisation " + self["name"] + " by " + user.get('name')  + " as a " + item["tag"]
            })
            notif.save()
            user = users.find_one({"_id":objectid.ObjectId(item.get("_id"))})
            user.get("pending_invitation").append({"type":"organisation", "id":str(self.get("_id"))})
            user.save()


### FEATURES : join, allow, leave, donate, createProject, createOffer, createProposal, voteForProposal, executeProposal, refreshProposals, endProposal (+all callbacks)
### STRUCTURE IS : 
### def doSomething(arg, ...):
###		function code
###		function code	

### def somethingDone(self, logs, callback_data=None):
###		callback_code

    def join(self, user, tag="member", password=None, local=False):
        """
        user : UserDoc initiating the action
        tag : string used to determine the rights of the new member
        password : password unlocking the account at the origin of the action
        local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
        Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
        Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
        """
        if not self.can(user, "join"):
            return False

        ## WE SHOULD CHECK RIGHT BEFORE BUT ITS NOT WORKING
        if self.get('rules').get('accessibility') == 'private':
            isAllowed = self.registry.call('isAllowed', local=True, args=[user.get('account')])
            if not isAllowed:
                return False

        tx_hash = self.registry.call('register', local=local, from_=user.get('account'), args=[user.get('account'), tag], password=password)
        if tx_hash and tx_hash.startswith('0x'):
            topics = makeTopics(self.registry.getAbi("NewMember").get('signature'), user.get('account'))

            mail = {'sender':self, 'subject':user, 'users':[user], 'category':'NewMember'} if user.get('notification_preference').get('NewMember').get('Mail') else None
            bw.pushEvent(LogEvent("NewMember", tx_hash, self.registry["address"], topics=topics, callbacks=[self.memberJoined, user.joinedOrga], users=user, event_abi=self.registry["abi"], mail=mail))
            #user.needsReloading()
            return tx_hash
        else:
            return False

    def memberJoined(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded and that the member isn't already part of the members, a new Member is created and stored in the orga document with its rights assigned
        The organisation is returned alongside the rights of the new member
        """
        if len(logs) == 1 and len(logs[0].get('topics')) == 2 and len(logs[0]["decoded_data"]) == 1:
            address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            new_member = users.find_one({"account": address})
            if new_member and new_member.get('account') not in self.get('members'):
                self.reload()
                rights_tag = logs[0]["decoded_data"][0]
                if rights_tag in self.get('rights').keys():
                    member_data = new_member.anonymous() if self.get('rules').get("anonymous") else new_member.public()
                    public_member =  models.member.Member(member_data, tag=rights_tag)
                    self["members"][new_member.get('account')] = public_member
                    notif = models.notification.NotificationDocument({
                                    "sender": {"id": new_member.get("_id"), "type": "user"},
                                    "subject": {"id": self.get("_id"), "type": "orga"},
                                    "category": "newMember",
                                                "angularState": {
                                        "route":"app.organization",
                                        "params":{
                                            "_id":str(self.get("_id")),
                                        "name":self.get("name")
                                        }
                                                },
                                                "description": new_member.get("name", address) + " has join the organization " + self["name"] + ".", 
                                                "createdAt": datetime.datetime.now(),
                                                "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")})
                    notif.save()
                    self.save_partial();
                    return { "orga": self.public(public_members=True), "rights": self.get('rights').get(public_member.get('tag'))}

        return False

    def allow(self, user, allowed_user, action, password=None, local=False):
        """
        user : UserDoc initiating the action
        password : password unlocking the account at the origin of the action
        local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
        Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
        Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
        """

        # if not self.can(user, "edit_rights"):
        # 	return False

        tx_hash = self.registry.call('allow', local=local, from_=user.get('account'), args=[allowed_user], password=password)
        if tx_hash and tx_hash.startswith('0x'):
            bw.pushEvent(LogEvent("PermissionChanged", tx_hash, self.registry["address"], callbacks=[self.permissionChanged], users=user, event_abi=self.registry["abi"]))
            #user.needsReloading()
            return tx_hash
        else:
            return False


    def permissionChanged(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded and that the member isn't already part of the members, a new Member is created and stored in the orga document with its rights assigned
        The organisation is returned alongside the rights of the new member
        """
        if len(logs) == 1 and len(logs[0].get('topics')) == 2 and len(logs[0]["decoded_data"]) == 1:
            address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            new_member = users.find_one({"account": address})
            member = self.getMember(address)
            return self
        return False


    def leave(self, user, password=None, local=False):
        """
        user : UserDoc initiating the action
        password : password unlocking the account at the origin of the action
        local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
        Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
        Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
        """
        if not self.can(user, "leave"):
            return False

        tx_hash = self.registry.call('leave', local=local, from_=user.get('account'), args=[user.get('account')], password=password)
        if tx_hash and tx_hash.startswith('0x'):
            topics = makeTopics(self.registry.getAbi("MemberLeft").get('signature'), user.get('account'))

            mail = {'sender':self, 'subject':user, 'users':[user], 'category':'MemberLeft'} if user.get('notification_preference').get('MemberLeft').get('Mail') else None
            bw.pushEvent(LogEvent("MemberLeft", tx_hash, self.registry["address"], topics=topics, callbacks=[self.memberLeft, user.leftOrga], users=user, event_abi=self.registry["abi"], mail=mail))
            #user.needsReloading()
            return tx_hash
        else:
            return False

    def removeMember(self, user, member_account, password=None, local=False):
        """
        user : UserDoc initiating the action
        password : password unlocking the account at the origin of the action
        local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
        Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
        Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
        """
        if not self.can(user, "remove_members"):
            return False
                
        member = users.find_one({"account": member_account})
        tx_hash = self.registry.call('leave', local=local, from_=user.get('account'), args=[member.get('account')], password=password)
        if tx_hash and tx_hash.startswith('0x'):
            topics = makeTopics(self.registry.getAbi("MemberLeft").get('signature'), member.get('account'))

            mail = {'sender':self, 'subject':member, 'users':[member], 'category':'MemberLeft'} if member.get('notification_preference').get('MemberLeft').get('Mail') else None
            bw.pushEvent(LogEvent("MemberLeft", tx_hash, self.registry["address"], topics=topics, callbacks=[self.memberLeft, member.leftOrga], users=member, event_abi=self.registry["abi"], mail=mail))
            #user.needsReloading()
            return tx_hash
        else:
            return False

                
    def memberLeft(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded and that the member is part of the members, remove it
        The organisation is returned alongside the rights of the user, which is no longer a member
        """
        if len(logs) == 1 and len(logs[0].get('topics')) == 2:
            address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            member = self.getMember(address)
            if member:
                del self["members"][address]
                self.save_partial();
                notif = models.notification.NotificationDocument({
                            "sender": {"id": member.get("_id"), "type": "user"},
                            "subject": {"id": self.get("_id"), "type": "orga"},
                            "category": "memberLeft",
                                        "angularState": {
                                "route":"app.organization",
                                "params":{
                                    "_id":str(self.get("_id")),
                                "name":self.get("name")
                                }
                                        },
                                        "description": member.get("name", address) + " has left the organization " + self["name"] + ".", 
                                        "createdAt": datetime.datetime.now(),
                                        "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")})
                notif.save()
                return { "orga": self.public(public_members=True), "rights": self.get('rights').get('default')}
        return False

    def donate(self, user, amount, password=None, local=False):
        """
        user : UserDoc initiating the action
        password : password unlocking the account at the origin of the action
        local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
        Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
        Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
        """
        if not self.can(user, "donate"):
            return False

        if toWei(user.refreshBalance()) < amount:
            return False
        tx_hash = self.board.call('donate', local=local, from_=user.get('account'), value=amount, password=password)
        if tx_hash and tx_hash.startswith('0x'):
            topics = makeTopics(self.board.getAbi("DonationMade").get('signature'), user.get('account'))

            mail = {'sender':self, 'subject':user, 'users':[user], 'category':'DonationMade'} if user.get('notification_preference').get('DonationMade').get('Mail') else None
            bw.pushEvent(LogEvent("DonationMade", tx_hash, self.board["address"], topics=topics, callbacks=[user.madeDonation, self.newDonation], users=user, callback_data={"name": self["name"]}, event_abi=self.board["abi"], mail=mail))
            #user.needsReloading()
            return tx_hash
        else:
            return False

    def newDonation(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded, add the amount of the donation to the member's data
        """
        if len(logs) == 1 and len(logs[0].get('topics')) == 3:
            donation_amount = fromWei(int(logs[0].get('topics')[2], 16))
            self["balance"] = self.getTotalFunds()

            address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            member = self.getMember(address)
            if member:
                self["members"][address]["donation"] = member.get('donation', 0) + donation_amount
                notif = models.notification.NotificationDocument({
                            "sender": {"id": member.get("_id"), "type": "user"},
                            "subject": {"id": self.get("_id"), "type": "orga"},
                            "category": "newDonation",
                                        "angularState": {
                                "route":"app.organization",
                                "params":{
                                    "_id":str(self.get("_id")),
                                "name":self.get("name")
                                }
                                        },
                                        "description": member.get("name", address) + " has made a donation of " + str(donation_amount) + " to the organization " + self["name"] + ".", 
                                        "amount": donation_amount,
                                        "createdAt": datetime.datetime.now(),
                                        "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")})
                self["transactions"][logs[0].get("transactionHash")] =  {"type": "Donation", "value": donation_amount, "flux": "In", "status": "Finished",
                                                                                         "note": "Donation of " + str(donation_amount) + " Ether as been made by " + member.get("name", address) + ".",
                                                                                         "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p"), "actor": address}                                
            else:
                notif = models.notification.NotificationDocument({
                            "sender": {"id": address, "type": "user"},
                            "subject": {"id": self.get("_id"), "type": "orga"},
                            "category": "newDonation",
                                        "angularState": {
                                "route":"app.organization",
                                "params":{
                                    "_id":str(self.get("_id")),
                                "name":self.get("name")
                                }
                                        },
                                        "description": address + " has made a donation of " + str(donation_amount) + " to the organization " + self["name"] + ".",                                         
                                        "amount": donation_amount,
                                        "createdAt": datetime.datetime.now(),
                                        "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")})
                self["transactions"][logs[0].get("transactionHash")] =  {"type": "Donation", "value": donation_amount, "flux": "In", "status": "Finished",
                                                                                         "note": "Donation of " + str(donation_amount) + " Ether as been made by " + address + ".",
                                                                                         "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p"), "actor": address}                                
            notif.save()
            self.save_partial()
            return self["balance"]
        return False

    def kill(self, from_):
        return None

    def createProject(self, user, project, password=None):
        """
        user : UserDoc initiating the action
        password : password unlocking the account at the origin of the action
        local : boolen set to True if the transaction is of type "call" (execution on local eth node), False if it is truly a transaction to be broadcasted on the network
        Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
        Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
        """
        if not self.can(user, "create_project"):
            return False
        tx_hash = self.board.call('createProject', local=False, from_=user.get('account'), args=[project.get('name', 'newProject'), int(project.get('campaign', {}).get('duration', 1))], password=password)

        if tx_hash and tx_hash.startswith('0x'):

            mail = {'sender':self, 'subject':user, 'users':[user], 'category':'ProjectCreated'} if user.get('notification_preference').get('ProjectCreated').get('Mail') else None
            bw.pushEvent(LogEvent("ProjectCreated", tx_hash, self.board["address"], callbacks=[self.projectCreated], users=user, event_abi=self.board["abi"], mail=mail, callback_data=project))
            #user.needsReloading()
            return tx_hash
        else:
            return False

    def projectCreated(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded, create a new ProjectDocument and save its data into the orga document
        """
        if len(logs) == 1 and len(logs[0].get('topics')) == 2:
            contract_address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            new_project = ProjectDocument(at=contract_address, contract='BaseProject', owner=self.public(), gen_skel=True)
            if callback_data:
                new_project.update(callback_data)
            new_project["contracts"] = dict()
            new_project["contracts"] = {
                "board": {"address": contract_address, "_id": new_project.board.save()},
                "registry": self["contracts"]["registry"]
            }
            new_project["balance"] = new_project.getTotalFunds()
            project_id = new_project.save()
            if contract_address not in self["projects"]:
                self["projects"][contract_address] = new_project
                self.save_partial()
                return {"project": new_project, "orga": self}
        return False

    def killProject(self, project):
        return None

    def createOffer(self, user, offer, password=None):
        """
        check if sender can create offer
        check if offer is valid (client == orga, ...)
        deploy offer contract and set callback
        return tx_hash
        """
        if not self.can(user, "create_offer"):
            return False

        try:
            offer["hashOfTheProposalDocument"] = sha3_256(offer["description"].encode()).hexdigest().encode('utf-8')[:32]
            offer["minDailyWithdrawalLimit"] = int(toWei(offer.get('recurrentWithdrawal')) / 30) if offer.get('isRecurrent') else 0
            offer['initialWithdrawal'] = int(toWei(offer['initialWithdrawal']))
            offer['payoutFreezePeriod'] = self.get('rules').get('payout_freeze_period', 0)
            args = [offer['contractor'], offer['client'], offer['hashOfTheProposalDocument'], offer['initialWithdrawal'], offer['minDailyWithdrawalLimit'], offer['payoutFreezePeriod'], offer['isRecurrent'], offer['duration'], offer['type']]
        except KeyError as e:
            return "missing param"

        tx_hash = self.board.call('createOffer', local=False, from_=user.get('account'), args=args, password=password)

        if tx_hash and tx_hash.startswith('0x'):
            mail = {'sender':self, 'subject':user, 'users':[user], 'category':'OfferCreated'} if user.get('notification_preference').get('OfferCreated').get('Mail') else None
            callback_data = {"description": offer.get('description'), "actors": offer.get('actors'), "name": offer.get('name')}
            bw.pushEvent(LogEvent("OfferCreated", tx_hash, self.board["address"], callbacks=[self.offerCreated], callback_data=callback_data, users=user, event_abi=self.board["abi"], mail=mail))
            #user.needsReloading()
            return tx_hash
        else:
            return False

    def offerCreated(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded, create a new ProjectDocument and save its data into the orga document
        """
        if len(logs) == 1 and len(logs[0].get('topics')) == 3:
            offer_address = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            contractor = normalizeAddress(logs[0].get('topics')[2], hexa=True)
            new_offer = Offer(at=offer_address, contract='Offer', owner=contractor, init_from_contract=True)
            new_offer["is_deployed"] = True
            new_offer.update(callback_data)
            new_offer["contract_id"] = new_offer.save()
            if offer_address not in self["proposals"]:
                self["transactions"][offer_address] =  {"type": "New Offer", "value": fromWei(float(new_offer["initialWithdrawal"])), "flux": "Out", "status": "pending",
                                                                        "note": users.find_one({"account": new_offer["owner"]}).get("name") + " created the " +  new_offer["contract_name"] + " '" + new_offer["name"] +
                                                                        "' for the organization.",
                                                                        "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p"), "actor": new_offer["owner"]}
                self["proposals"][offer_address] = Proposal(doc={"offer": new_offer, "status": "pending"})
                self.save_partial()
                return self
        return False

    def cancelOffer(self, user, offer, password=None):
        """
        a user can cancel its own offer
        """
        tx_hash = self.board.call('cancelOffer', local=False, from_=user.get('account'), args=[offer.get('name', 'newProject')], password=password)

        if tx_hash and tx_hash.startswith('0x'):
            mail = {'sender':self, 'subject':user, 'users':[user], 'category':'OfferCanceled'} if user.get('notification_preference').get('OfferCanceled').get('Mail') else None
            bw.pushEvent(LogEvent("OfferCanceled", tx_hash, self.board["address"], callbacks=[], users=user, event_abi=self.board["abi"], mail=mail))
            #user.needsReloading()
            return tx_hash
        else:
            return False

    def createProposal(self, user, offer_addr, duration, password=None):
        """
        canSenderPropose
        check proposal (_name, _type, , _description, _debatePeriod, _destination, _value, _calldata)
        destination is a valid offer from orga
        deploy proposal contract and set callback
        return tx_hash
        """
        offer = self['proposals'][offer_addr]["offer"]
        try:
            # value = str(int(offer.get('initialWithdrawal')) + int(offer.get('dailyWithdrawalLimit')) * 30 * int(offer.get('duration')))
            value = int(offer.get('initialWithdrawal')) + int(offer.get('dailyWithdrawalLimit')) * 30
            calldata = "sign()".encode('utf-8')#encode_hex(eth_cli._encode_function('sign()', [])).encode('utf-8')
            # calldata = (encode_hex(eth_cli._encode_function('sign()', []))).encode('utf-8')
            callvalue = (offer_addr + str(value) + calldata.decode()).encode()
            hashed_callvalue = sha3_256(callvalue).hexdigest().encode('utf-8')[:32]
            args = [offer['name'], duration or self["rules"]["default_proposal_duration"], offer_addr, value, calldata]
        except KeyError:
            return False
        tx_hash = self.board.call('newProposal', local=False, from_=user.get('account'), args=args, password=password)
        if tx_hash and tx_hash.startswith('0x'):
            mail = {'sender':self, 'subject':user, 'users':[user], 'category':'ProposalCreated'} if user.get('notification_preference').get('ProposalCreated').get('Mail') else None
            callback_data = {'calldata': calldata.decode('utf-8')}
            bw.pushEvent(LogEvent("ProposalCreated", tx_hash, self.board["address"], callbacks=[self.proposalCreated], callback_data=callback_data, users=user, event_abi=self.board["abi"], mail=mail))
            #user.needsReloading()
            return tx_hash
        else:
            return False


    def proposalCreated(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded, create a new ProjectDocument and save its data into the orga document
        """
        if len(logs) == 1 and len(logs[0].get('topics')) == 4:
            proposal_id = int(logs[0].get('topics')[1], base=16)
            destination = normalizeAddress(logs[0].get('topics')[2], hexa=True)
            value = int(logs[0].get('topics')[3], base=16)
            if destination in self["proposals"]:
                new_proposal = Proposal(doc={"proposal_id": proposal_id}, board=self.board, init_from_contract=True)
                self["proposals"][destination].update(new_proposal)
                self["proposals"][destination].update(callback_data)
                self["proposals"][destination]["status"] = "debating"
                self["proposals"][destination]["votes_count"] = 0
                self["proposals"][destination]["participation"] = 0
                self["proposals"][destination]["time_left"] = 100

                offer_contract = models.contract.contracts.find_one({"_id": self["proposals"][destination]["offer"].get('_id')})
                self["proposals"][destination]["offer"]["votingDeadline"] = offer_contract.call('getVotingDeadline', local=True)
                self.save_partial()
                return self
        return False


    def voteForProposal(self, user, proposal_id, vote, password=None):
        """
        can sender vote
        send tx and return hash
        """
        tx_hash = self.board.call('vote', local=False, from_=user.get('account'), args=[proposal_id, vote], password=password)

        if tx_hash and tx_hash.startswith('0x'):
            bw.pushEvent(LogEvent("VoteCounted", tx_hash, self.board["address"], callbacks=[self.voteCounted], users=user, event_abi=self.board["abi"]))
            #user.needsReloading()
            return tx_hash
        else:
            return False

    def voteCounted(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded, create a new ProjectDocument and save its data into the orga document
        """
        if len(logs) == 1 and len(logs[0].get('topics')) == 4:
            destination = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            position = int(logs[0].get('topics')[2], base=16)
            voter = normalizeAddress(logs[0].get('topics')[3], hexa=True)
            vote = self.board.call('voteOf', local=True, args=[self["proposals"][destination]["proposal_id"], voter])

            member = self.getMember(voter)
            if member:
                member.saveVotes(destination, vote)
            if destination in self["proposals"]:
                self["proposals"][destination]["votes_count"] += 1
                self["proposals"][destination]["participation"] += (1 / len(self["members"])) * 100

                time_since_creation = datetime.datetime.utcnow().timestamp() - self["proposals"][destination]["created_on"]
                self["proposals"][destination]["time_left"] = 100 - int((time_since_creation / self["proposals"][destination]["debate_period"]) * 100)

                self.save_partial()
                return {'orga': self, 'user': member}
        return False



    def refreshProposals(self):
        """
        compute quorum and time left for a proposal and return the new list
        """
        for proposal in self["proposals"].values():
            if proposal["status"] == "debating":
                time_since_creation = datetime.datetime.utcnow().timestamp() - proposal["created_on"]
                proposal["time_left"] = 100 - int((time_since_creation / proposal["debate_period"]) * 100)
                if proposal["time_left"] < 0:
                    self.endProposal(proposal)
        self.save_partial()
        return self

    def endProposal(self, proposal):

        proposal["nay"] = self.board.call('positionWeightOf', local=True, args=[proposal["proposal_id"], 0])
        proposal["yea"] = self.board.call('positionWeightOf', local=True, args=[proposal["proposal_id"], 1])

        proposal["score"] = (float(proposal["yea"] / (proposal["yea"] + proposal["nay"])) * 100) if proposal["participation"] > 0 else 0

        if proposal["yea"] > proposal["nay"]\
           and proposal["participation"] >= self["rules"]["quorum"]\
           and proposal["score"] >= self["rules"]["majority"]:
            proposal["status"] = "approved"
            self["transactions"][proposal["offer"]["address"]]["status"] = "approved"
        else:
            self["transactions"][proposal["offer"]["address"]]["status"] = "denied"
            proposal["status"] = "denied"

    def getProposal(self, proposal_id):
        for p in self.get('proposals', {}).values():
            if p.get('proposal_id') == proposal_id:
                return p

    def executeProposal(self, user, proposal_id, password=None):
        """
        if proposal is finished and not executed
        sen tx and return hash
        """
        p = self.getProposal(proposal_id)
        tx_hash = self.board.call('execute', local=False, from_=user.get('account'), args=[proposal_id, p.get('calldata').encode()], password=password)
        if tx_hash and tx_hash.startswith('0x'):
            bw.pushEvent(LogEvent("ProposalExecuted", tx_hash, self.board["address"], callbacks=[self.proposalExecuted, user.proposalExecuted], callback_data=p, users=user, event_abi=self.board["abi"]))
            #user.needsReloading()
            return tx_hash
        else:
            return False

    def proposalExecuted(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded, create a new ProjectDocument and save its data into the orga document
        """
        if len(logs) == 1 and len(logs[0].get('topics')) == 3:
            proposal_id = int(logs[0].get('topics')[1], base=16)
            destination = normalizeAddress(logs[0].get('topics')[2], hexa=True)
            # call_data = logs[0].get('topics')[3]

            if destination in self["proposals"]:
                self["proposals"][destination]["executed"] = True
                self["transactions"][destination]["status"] = "accepted and finished"
                self.save_partial()
                return self
        return False

    def withdrawFundsFromOffer(self, user, offer, password=None):
        """
        """

        tx_hash = offer.call('withdraw', local=False, from_=user.get('account'), password=password)
        if tx_hash and tx_hash.startswith('0x'):
            bw.pushEvent(LogEvent("FundsWithdrawn", tx_hash, offer["address"], callbacks=[self.fundsWithdrawnFromOffer], callback_data=offer, users=user, event_abi=self.board["abi"]))
            #user.needsReloading()
            return tx_hash
        else:
            return False

    def fundsWithdrawnFromOffer(self, logs, callback_data=None):
        """
        logs : list of dict containing the event's logs
        If the transaction has succeeded, create a new ProjectDocument and save its data into the orga document
        """

        if len(logs) == 1 and len(logs[0].get('topics')) == 3:
            withdrawal_amount = int(logs[0].get('topics')[2], base=16)
            destination = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            print("balance == ", fromWei(eth_cli.eth_getBalance(destination)), " and withdrawal amount ", fromWei(withdrawal_amount))
            self["transactions"][callback_data["address"]] =  {"type": "Offer withdrawal", "value": fromWei(withdrawal_amount), "flux": "Out", "status": "Finished",
                                                                           "note": "The contractor " + users.find_one({"account": callback_data["contractor"]}).get("name") +
                                                                           " has withdraw" + str(fromWei(withdrawal_amount)) + " from the contract '" + callback_data["name"] + "'.",
                                                                           "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p"), "actor": callback_data["contractor"]}
            self.save_partial()
            return {'orga': self, 'withdrawal': "You received %d ether (%d wei) in your wallet" % (fromWei(withdrawal_amount), withdrawal_amount)}
        return False


    def changeConstitution(self, user, constitution):
        """
        deploy new Rules contract and call changeRules with the address of the new contract
        """
        return None


class OrgaCollection(Collection):
    """
    Abstraction of the 'organizations' mongo collection
    Overrides a mongokat.Collection
    """

    document_class = OrgaDocument

    orga_info = [
        ""
    ]

    public_info = [
        "_id",
        "address",
        "name",
        "contract_id",
        "description",
        "balance",
        "social_accounts",
        "contracts"
    ]

    structure = {
        "name": str,
        "members": dict,
        "rights": dict,
        "rules": dict,
        "proposals": dict,
        "projects": dict,
        "description": str,
        "owner": dict,
        "contracts": dict,
        "files": dict,
        "tx_history": list,
        "creation_date": str,
        "mailing_lists": dict,
        "transactions": dict,
        "accounting_data": str,
        "alerts": list,
        "social_accounts": dict,
        "balance": int,
        "uploaded_documents": list,
        "gov_model": str,
        "invited_users": dict,
        "news": list
    }

    def lookup(self, query):
        """
        query : either a string or a regex
        Look for a name matching 'query'
        Returns the list of the results. Each result is tagged with a flag {"category": "organization"}
        """
        print("SEARCH FOR ORGA:: ", query)
        results = list(super().find({"name": query, "rules.hidden": False}, ["_id", "name", "address"]))
        for doc in results:
            doc.update({"category": "organization"})
        return results

    @find_method
    def find_one(self, *args, **kwargs):
        """
        args : see mongokat.Collection.find_one
        kwargs : see mongokat.Collection.find_one
        Overload the parent find_one function to initialize the Contract object which has its _id contained in the orga document
        """
        from .orga_models import governances

        doc = super().find_one(*args, **kwargs)
        if doc and doc.get("gov_model"):
            doc = governances[doc["gov_model"]]["templateClass"](doc)
            doc.__init__()
        return doc

organizations = OrgaCollection(collection=client.main.organizations)
