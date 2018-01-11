from hashlib import sha3_256
from ..organization import OrgaDocument as Organization
import models.notification
from bson import objectid
import datetime
from models.user import users, UserDocument as User
from core.utils import fromWei, toWei, normalizeAddress

from models.events import ContractCreationEvent, LogEvent

from bson import ObjectId
from models.clients import client, eth_cli, blockchain_watcher as bw


class PublicCompany(Organization):

    default_rules = {
        "default_proposal_duration": 80,
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
            "weight": 3,
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
            "weight": 1,
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
            "publish_news": True,
            "edit_rights": True,
            "edit_jobs": True,
            "access_administration": True
        },
        "default": {
            "weight": 1,
            "join": False,
            "leave": False,
            "donate": True,
            "create_project": True,
            "create_offer": True,
            "create_proposal": True,
            "vote_proposal": True,
            "recruit": False,
            "remove_members": False,
            "sell_token": True,
            "buy_token": True,
            "publish_news": True,
            "edit_rights": False,
            "edit_jobs": False,
            "access_administration": False
        }
    }

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

            token_props = self.get('token')
            amount = token_props.get('amount')
            price = toWei(token_props.get('price'))
            owned_part = int(
                amount * float(int(token_props.get('owned')) / 100))
            token_contract_args = [amount, price, owned_part, token_props.get(
                'name'), 0, token_props.get('short')]
            print("sending token args", token_contract_args)
            tx_hash = self.token.deploy(
                from_.get('account'), args=token_contract_args)

            bw.waitTx(tx_hash)
            token_contract_address = eth_cli.eth_getTransactionReceipt(
                tx_hash).get('contractAddress')
            self.token["address"] = token_contract_address
            self.token["is_deployed"] = True
            self.token["initial_price"] = token_props.get('price')
            print("Token is mined !", token_contract_address)
            balances_token = {
                "contract": self.token.call("balanceOf", local=True, args=[self.token["address"]]),
                "owner": self.token.call("balanceOf", local=True, args=[from_.get('account')])
            }
            balances_eth = {
                "contract": fromWei(self.token.getBalance()),
                "owner": from_.refreshBalance()
            }
            print("tokens : ", balances_token)
            print("eth : ", balances_eth)
            from_.unlockAccount(password=password)
            tx_hash = self.token_freezer.deploy(
                from_.get('account'), args=[self.token["address"]])
            bw.waitTx(tx_hash)
            token_freezer_contract_address = eth_cli.eth_getTransactionReceipt(
                tx_hash).get('contractAddress')
            self.token_freezer["address"] = token_freezer_contract_address
            self.token_freezer["is_deployed"] = True
            print("Token Freezer is mined !", token_contract_address)
        except AttributeError:
            pass

        from_.unlockAccount(password=password)
        tx_hash = self.rules.deploy(from_.get('account'), args=[
                                    self.token_freezer["address"], list(), 0])
        bw.waitTx(tx_hash)
        print("Rules are mined !", eth_cli.eth_getTransactionReceipt(
            tx_hash).get('contractAddress'))
        self.rules["address"] = eth_cli.eth_getTransactionReceipt(
            tx_hash).get('contractAddress')
        self.rules["is_deployed"] = True
        args.append(self.rules["address"])
        args.append(0)
        from_.unlockAccount(password=password)
        tx_hash = self.board.deploy(from_.get('account'), args=args)

        action = {
            "action": "donate",
            "from": from_,
            "password": password,
            "initial_funds": self.get('initial_funds')
        }

        bw.pushEvent(ContractCreationEvent(
            tx_hash=tx_hash, callbacks=self.register, callback_data=action, users=from_))
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

        # ADD OWNER
        from_ = callback_data.get('from')

        # CONFIGURE BOARD
        # tx_hash = self.rules.call("configureBoard", local=False, from_=from_.get(
        #     'account'), args=[self.board["address"]], password=callback_data.get('password'))
        # bw.waitTx(tx_hash)
        # print("BOARD IS CONFIGURED !", self.rules.call(
        #     "isConfigured", local=True, args=[self.board["address"]]), tx_hash)

        # SEND FUNDS TO ORGA AFTER IT IS CREATED
        if callback_data and callback_data.get('action') == "donate" and callback_data.get("initial_funds", 0) > 0:
            amount = float(callback_data.get('initial_funds'))
            if from_.refreshBalance() > amount:
                from_.session_token = None
                from_.unlockAccount(password=callback_data.get('password'))
                tx_hash = self.donate(from_, toWei(
                    amount), password=callback_data.get('password'), local=False)
                if not tx_hash:
                    return {"data": "User does not have permission to donate", "status": 400}
            else:
                return {"data": "Not enough funds in your wallet to process donation", "status": 400}

        self["balance"] = self.getTotalFunds()

        self["contracts"] = dict()
        for contract_type, contract_instance in {k: v for k, v in {"board": self.board, "rules": self.rules, "registry": self.registry, "token": self.token, 'token_freezer': self.token_freezer}.items() if v is not None}.items():
            self["contracts"][contract_type] = {
                "address": contract_instance["address"],
                "_id": contract_instance.save()
            }
        self.save()

        for item in self.get('invited_users'):
            print(item)
            notif = models.notification.NotificationDocument({
                "sender": {"id": objectid.ObjectId(self.get("_id")), "type": "organization"},
                "subject": {"id": objectid.ObjectId(item), "type": "user"},
                "category": "newInviteJoinOrga",
                "angularState": {
                    "route": "app.organization",
                    "params": {
                        "_id": str(self.get("_id")),
                        "name": self.get("name")
                    }
                },
                "description": "You have been invited in the organisation " + self["name"] + " by " + callback_data.get('from')["name"] + " as a " + self.get("invited_users").get(item)["tag"]
            })
            notif.save()
            user = users.find_one({"_id": objectid.ObjectId(item)})
            user.get("pending_invitation").append(
                {"type": "organisation", "id": str(self.get("_id"))})
            user.save()

        resp = {"name": self["name"], "_id": str(self["_id"])}
        resp.update(
            {"data": {k: str(v) if type(v) == ObjectId else v for (k, v) in self.items()}})
        notif = models.notification.NotificationDocument({
            "sender": {"id": objectid.ObjectId(resp.get("data").get("_id")), "type": "orga"},
            "subject": {"id": objectid.ObjectId(resp.get("data").get("owner").get("_id")), "type": "user"},
            "category": "orgaCreated",
            "angularState": {
                "route": "app.organization",
                "params": {
                    "_id": str(self.get("_id")),
                        "name": self.get("name")
                }
            },
            "description": "The organization " + self["name"] + "was created by " + callback_data.get('from')["name"] + ".",
            "createdAt": datetime.datetime.now(),
            "date": datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")})
        notif.save()
        print("BUYING TOKEN")
        self.buyToken(from_, 10, None, None,
                      password=callback_data.get('password'))
        return resp

    def buyToken(self, from_, amount, price, seller, password=None, local=False):
        """
        from_ : UserDoc initiating the action
        amount : amount of tokens to buy
        price : unit price for a token (in eth)
        seller : addr of seller who sent a specific offer
        Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
        Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
        """
        if not self.can(from_, "buy_token"):
            return False

        if seller is None:
            seller = self.token["address"]

        if price is None:
            price = self.token["initial_price"]

        total_price = toWei(price) * amount

        if toWei(from_.refreshBalance()) < total_price:
            return False

        print("sending tx with", amount, seller, total_price, password)
        tx_hash = self.token.call('buy', local=local, from_=from_.get(
            'account'), args=[amount, seller], value=total_price, password=password)

        if tx_hash and tx_hash.startswith('0x'):
            if seller == self.token["address"]:
                bw.pushEvent(LogEvent("Transfer", tx_hash, self.token["address"], callbacks=[
                    self.boughtToken], users=from_, callback_data=from_, event_abi=self.token["abi"]))
            else:
                bw.pushEvent(LogEvent("NewBuyOrder", tx_hash, self.token["address"], callbacks=[
                    self.sentOrder], users=from_, callback_data=from_, event_abi=self.token["abi"]))

            return tx_hash
        return False

    def boughtToken(self, logs, callback_data=None):
        if len(logs) == 1 and len(logs[0].get('topics')) == 4:
            seller = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            to_ = normalizeAddress(logs[0].get('topics')[2], hexa=True)
            value = int(logs[0].get('topics')[3], base=16)
            print("LOGS:", seller, to_, value)
            balances_token = {
                "contract": self.token.call("balanceOf", local=True, args=[self.token["address"]]),
                "owner": self.token.call("balanceOf", local=True, args=[callback_data.get('account')])
            }
            balances_eth = {
                "contract": fromWei(self.token.getBalance()),
                "owner": callback_data.refreshBalance()
            }
            print("tokens : ", balances_token)
            print("eth : ", balances_eth)
            self.sellToken(callback_data, 30, price=10,
                           password="simon")
        return self

    def sellToken(self, from_, amount, price=None, to_=None, password=None, local=False):
        """
        from_ : UserDoc initiating the action
        amount : amount of tokens to buy
        price : unit price for a token (in eth)
        Sends the transaction to the smart contract, pushes new event to wait for the result of the tx.
        Returns the transaction hash if the tx is successfully sent to the node, False otherwise (eg: not enough funds in account)
        """
        if not self.can(from_, "buy_token"):
            return False

        if to_ is None and price is not None:
            unit_price = toWei(price)
            print("sending tx with", from_.get(
                'account'), amount, unit_price, password)
            tx_hash = self.token.call('sell', local=local, from_=from_.get(
                'account'), args=[amount, unit_price], password=password)

            if tx_hash and tx_hash.startswith('0x'):
                bw.pushEvent(LogEvent("SellOrder", tx_hash, self.token["address"], callbacks=[
                    self.sentOrder], users=from_, callback_data=from_, event_abi=self.token["abi"]))
                return tx_hash

        elif price is None and to_ is not None:
            unit_price = toWei(price)
            print("sending tx with", from_, amount, unit_price, password)
            tx_hash = self.token.call('sellTo', local=local, from_=from_.get(
                'account'), args=[to_], password=password)

            if tx_hash and tx_hash.startswith('0x'):
                bw.pushEvent(LogEvent("Transfer", tx_hash, self.token["address"], callbacks=[
                    self.soldToken], users=from_, callback_data=from_, event_abi=self.token["abi"]))
                return tx_hash

        return False

    def soldToken(self, logs, callaback_data):
        if len(logs) == 1 and len(logs[0].get('topics')) == 4:
            seller = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            to_ = normalizeAddress(logs[0].get('topics')[2], hexa=True)
            value = int(logs[0].get('topics')[3], base=16)
            print("LOGS:", seller, to_, value)
        return self

    def sentOrder(self, logs, callback_data=None):
        if len(logs) == 1 and len(logs[0].get('topics')) == 4:
            from_ = normalizeAddress(logs[0].get('topics')[1], hexa=True)
            amount = int(logs[0].get('topics')[2], base=16)
            price = int(logs[0].get('topics')[3], base=16)
            print("LOGS:", from_, amount, price)
            balances_token = {
                "contract": self.token.call("balanceOf", local=True, args=[self.token["address"]]),
                "owner": self.token.call("balanceOf", local=True, args=[callback_data.get('account')])
            }
            balances_eth = {
                "contract": fromWei(self.token.getBalance()),
                "owner": callback_data.refreshBalance()
            }
            print("tokens : ", balances_token)
            print("eth : ", balances_eth)
        return self

    def createProposal(self, user, offer_addr, duration, password=None):
        """
        canSenderPropose
        check proposal (_name, _type, , _description, _debatePeriod, _destination, _value, _calldata)
        destination is a valid offer from orga
        deploy proposal contract and set callback
        return tx_hash
        """
        bal = self.token_freezer.call(
            "balanceOf", local=True, args=[user.get('account')])

        offer = self['proposals'][offer_addr]["offer"]
        print("can is ", bal, offer)

        try:
            print(1)
            value = int(offer.get('initialWithdrawal')) + \
                int(offer.get('dailyWithdrawalLimit')) * 30
            calldata = "sign()".encode('utf-8')
            callvalue = (offer_addr + str(value) + calldata.decode()).encode()
            hashed_callvalue = sha3_256(
                callvalue).hexdigest().encode('utf-8')[:32]
            print(1)
            args = [offer['name'], duration or self["rules"]
                    ["default_proposal_duration"], offer_addr, value, calldata]
            print(offer["name"],  self["rules"]["default_proposal_duration"])
        except KeyError:
            return False
        tx_hash = self.board.call('newProposal', local=False, from_=user.get(
            'account'), args=args, password=password)
        if tx_hash and tx_hash.startswith('0x'):
            mail = {'sender': self, 'subject': user, 'users': [user], 'category': 'ProposalCreated'} if user.get(
                'notification_preference').get('ProposalCreated').get('Mail') else None
            callback_data = {'calldata': calldata.decode('utf-8')}
            bw.pushEvent(LogEvent("ProposalCreated", tx_hash, self.board["address"], callbacks=[
                         self.proposalCreated], callback_data=callback_data, users=user, event_abi=self.board["abi"], mail=mail))
            # user.needsReloading()
            return tx_hash
        else:
            return False
