import scrypt
from bson.objectid import ObjectId
from core import SALT_WALLET_PASSWORD
from core.utils import fromWei
from flask import session
from mongokat import Collection, Document
from rlp.utils import encode_hex

from .clients import client, eth_cli

"""
This module implements the UserDoc class alongside with all its methods
"""


class UserDocument(Document):
    default_notifications = {}

    """
	Overrides a mongokat.Document and add custom methods
	This class is used everytime a controller needs to manipulate a user (and everytime a used sends a request with an authentification token)
	"""

    def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=False, session=None, notifs=True):
        """
		doc : dict containing the data to be initialized from
		mongokat_collection : see mongokat.Document (mongo collection associated with the doc)
		fetched_fileds : see mongokat.Document
		gen_skel : boolean. If set to true, the document is initialized with the fields described in OrgaCollection.structure
		session : token associated with the user's session
		notifs : bool True if we want the user to receive notifs
		"""
        super().__init__(doc, users, fetched_fields, gen_skel)
        if gen_skel:
            if not self.get('notification_preference'):
                self.generateDefaultNotification(activate=notifs)
        self.session_token = session

    def generateDefaultNotification(self, activate=True):
        for k, v in models.notification.notifications.descriptions.items():
            self.get("notification_preference")[k] = {"Web": activate, "Mobile": activate, "Mail": activate}

    def needsReloading(self):
        """
		This function is called when a transaction is sent to the eth node. The for this is that when the callback is called, the UserDoc data is modified in mongo but not in the session
		At the next request by the same user, the session will reload its data directly from the database.
		"""
        if self.session_token:
            session[self.session_token]["needs_reloading"] = True

    def reload(self):
        """
		Reloads the document from the database
		"""
        if self['_id'] and type(self['_id']) is str:
            self['_id'] = ObjectId(self.get('_id')) if type(self.get('_id')) is str else self['_id']
        super().reload()

    def save_partial(self, data=None, allow_protected_fields=False, **kwargs):
        """
		Save the fields currently set in the object in the db. Other fields remain untouched.
		"""
        if self['_id'] and type(self['_id']) is str:
            self['_id'] = ObjectId(self.get('_id')) if type(self.get('_id')) is str else self['_id']
        super().save_partial(data, allow_protected_fields, **kwargs)

    # CALLBACKS FOR UPDATE

    def joinedOrga(self, logs, callback_data=None):
        """
		logs : list of dict containing the event's logs
		If the transaction has succeeded and that the orga isn't already in the member's orga, the public orga data is stored in the user document
		None is returned if everything went fine, False otherwise
		"""
        if len(logs) == 1 and logs[0].get('address') is not None:
            address = logs[0].get('address')
            orga = models.organization.organizations.find_one({"address": address})
            if not orga:
                orga = models.organization.organizations.find_one({"contracts.registry.address": address})
            if orga and orga.public() not in self["organizations"]:
                self["organizations"].append(orga.public())
                self.save_partial();
            else:
                return False
        return None

    def joinedProject(self, logs, callback_data=None):
        """
		logs : list of dict containing the event's logs
		If the transaction has succeeded and that the orga isn't already in the member's orga, the public orga data is stored in the user document
		None is returned if everything went fine, False otherwise
		"""
        if len(logs) == 1 and logs[0].get('address') is not None:
            address = logs[0].get('address')
            proj = models.project.projects.find_one({"address": address})
            if not proj:
                proj = models.project.projects.find_one({"contracts.registry.address": address})
            if proj and proj.get('address') not in self["projects"]:
                self["projects"].append(proj.get('address'))
                self.save_partial();
            else:
                return False
        return None

    def leftOrga(self, logs, callback_data=None):
        """
		logs : list of dict containing the event's logs
		If the transaction has succeeded and that the orga is in the member's orga, the orga is removed
		None is returned if everything went fine, False otherwise
		"""
        if len(logs) == 1 and logs[0].get('address') is not None:
            address = logs[0].get('address')
            orga = models.organization.organizations.find_one({"address": address})
            if not orga:
                orga = models.organization.organizations.find_one({"contracts.registry.address": address})

            for o in self.get("organizations", []):
                if o.get('contracts').get('registry').get('address') == orga.get('contracts').get('registry').get(
                        'address'):
                    self["organizations"].remove(o)
                    self.save_partial();
                    return None
            return False
        return None

    def leftProject(self, logs, callback_data=None):
        """
		logs : list of dict containing the event's logs
		If the transaction has succeeded and that the orga is in the member's orga, the orga is removed
		None is returned if everything went fine, False otherwise
		"""
        if len(logs) == 1 and logs[0].get('address') is not None:
            address = logs[0].get('address')
            proj = models.project.projects.find_one({"address": address})
            if not proj:
                proj = models.project.projects.find_one({"contracts.registry.address": address})

            if proj and proj.get('address') in self["projects"]:
                self["projects"].remove(proj.get('address'))
                self.save_partial();
            else:
                return False
        return None

    def madeDonation(self, logs, callback_data=None):
        """
		logs : list of dict containing the event's logs
		If the transaction has succeeded, the total amount of donation is incremented by the value of the new one
		None is returned
		"""
        if len(logs) == 1 and len(logs[0].get('topics')) == 3:
            donation_amount = fromWei(int(logs[0].get('topics')[2], 16))
            self["donations"] = self.get('donations', 0) + donation_amount
            self.save_partial()
        return None

    # KEY MANAGEMENT

    def unlockAccount(self, password=None):
        """
		password : password to unlock the account
		There are different types of account, based on how they have been created. An account can either be :
			remote_hashed : means the user created key at account creation and his wallet password is the same as his Societhy account
			local_hashed : means the user created its wallet independently and created its own password.
			local : means the user imported its wallet and that the password is not a hash
		Once the password has been correctly formatted, unlock the account and return a boolean for the success of the action
		"""
        if not self.get('account'):
            return False
        elif self["password_type"] == "remote_hashed":
            password = self.hashPassword(self['password'])
        elif self["password_type"] == "local_hashed" and password is not None:
            password = self.hashPassword(password)
        elif self["password_type"] == "local" and password is not None:
            password = password

        if password is not None:
            return eth_cli.personal_unlockAccount(self["account"], password)
        else:
            return False

    def hashPassword(self, password):
        """
		password : string to hash
		Returns a hash of the string passed as parameter, using the scrypt algorithm and a fixed salt
		"""
        return encode_hex(scrypt.hash(password, SALT_WALLET_PASSWORD))

    def populateKey(self):
        """
		Generates and add a key to the user based on the existing password (Societhy account)
		"""
        from core.keys import genBaseKey
        newKey = genBaseKey(self["password"])
        if newKey:
            self.addKey(newKey.get('address'), local_account=False, password_type="remote_hashed",
                        keyfile=newKey.get('file'))
        else:
            self["account"] = None
            self["eth"] = {"keys": {}}
        self.save_partial()

    def generatePersonalDataFromSocial(self):
        """
		Uses social media account (if exists) to populate personal informations in the document
		"""
        fields = {"firstname", "lastname", "pictureURL", "email", "company"}
        if 'social' in self:
            for socialProvider, socialData in self['social'].items():
                for key, value in socialData.items():
                    if key in fields:
                        self[key] = value
        self.save_partial()

    def setDefaultKey(self, account):
        """
		account : address to be used as main account
		Set the key with public key "account" as the main one (the one used in all transactions)
		"""
        if account in self.get('eth').get('keys'):
            defaultKey = self["eth"]["keys"][account]
            self["account"] = defaultKey.get('address')
            self["local_account"] = defaultKey.get('local_account')
            self["password_type"] = defaultKey.get('password_type')
            self.save_partial()

    def addKey(self, account, local_account, password_type, balance=0, keyfile=None):
        """
		account : address of the account
		local_account : boolean. True if the key file is not stored on the server
		password_type : string. See unlockAccount method for more info
		balance : balance for the given account
		keyfile : name of the file if local_account is False. Defaults to None.
		Add a new key to the user's keyring with parameters. If the key 'account' is the first one to be added, it is set as the main (=default) one.
		"""
        if self.get('account') is None:
            self["account"] = account
            self["local_account"] = local_account
            self["password_type"] = password_type

        if not self.get('eth'):
            self["eth"] = {"keys": {}}

        self["eth"]["keys"][account] = {
            "balance": balance,
            "local_account": local_account,
            "password_type": password_type,
            "address": account,
            "file": keyfile
        }
        self.save_partial()

    def removeKey(self, key, local_account):
        """
		key : address of the account
		local_account : True if the keyfile is not stored on the webserver
		"""
        for publicKey in self["eth"]["keys"].keys():
            if publicKey == key:
                del self["eth"]["keys"][publicKey]
                if self["account"] == key:
                    self["account"] = None
                    self["local_account"] = None
                    self["password_type"] = None
                self.save_partial()
                return

    def getKey(self, publicKey=None):
        """
		publicKey : address
		Returns the main account's address. If publicKey is specified, returns the key data corresponding to the address if it is contained in the user's keyring, otherwise None
		"""
        if publicKey is None:
            return self.get('account')
        else:
            for key in self.get('eth').get('keys').keys():
                if key == publicKey:
                    return self.get('eth').get('keys').get(key)
            return None

    def refreshBalance(self, address=None):
        """
		address : address of the account for which the balance is retrieved
		Refreshes the balance of the user, the main one by default or 'address' if specified.
		The balance is returned.
		"""
        address = address or self.get('account')
        if address:
            balance = fromWei(eth_cli.eth_getBalance(address))
            if address in self['eth']['keys']:
                self['eth']['keys'][address]["balance"] = balance
                self.save_partial()
            return balance
        return None

    def public(self):
        """
		Returns the public information on the user
		"""
        return {
            key: self.get(key) for key in self if key in users.public_info
        }

    def anonymous(self):
        """
		Returns the private information on the user
		"""
        return {
            key: self.get(key) for key in self if key in users.anonymous_info
        }

    def delete(self):
        """
		Remove this user from the db.
		"""
        return self.mongokat_collection.remove({"_id": ObjectId(self.get('_id'))})

    def wantNotif(self, event, notif_type):
        return self["notification_preference"][event][notif_type]

class UserCollection(Collection):
    """
	Abstraction of the 'users' mongo collection
	Overrides a mongokat.Collection
	"""
    user_info = [
        "_id",
        "name",
        "address",
        "account",
        "local_account",
        "password_type",
        "eth",
        "eth.keys",
        "email",
        "gender",
        "firstname",
        "lastname",
        "city",
        "votes",
        "contact_list",
        "organizations",
        "notification_preference",
        "pending_invitation"
    ]

    public_info = [
        "_id",
        "name",
        "account",
        "firstname",
        "lastname",
        "organizations"
    ]

    anonymous_info = [
        "_id",
        "account"
    ]

    structure = {
        "name": str,
        "address": str,
        "account": str,
        "local_account": str,
        "password_type": str,
        "eth": dict,
        "email": str,
        "gender": str,
        "firstname": str,
        "lastname": str,
        "city": str,
        "contact_list": list,
        "organizations": list,
        "projects": list,
        "pending_invitation": list,
        "notification_preference": dict,
        "votes": list
    }

    document_class = UserDocument

    def lookup(self, query):
        """
		query : either a string or a regex
		Look for a name matching 'query'
		Returns the list of the results. Each result is tagged with a flag {"category": "user"}
		"""
        results = list(super().find({"name": query}, ["_id", "name", "account"]))
        for doc in results:
            doc.update({"category": "user"})
        return results


users = UserCollection(collection=client.main.users)

import models.organization
import models.project
import models.notification
