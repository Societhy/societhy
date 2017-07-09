import pytest
import sys
import time
from time import sleep
from os import environ, listdir, path, remove
from random import randint
from models.clients import client, eth_cli, blockchain_watcher as bw
from core import keys
from core import base_orga
from mongokat import Collection, Document


from models.user import users, UserDocument
from models.organization import organizations, OrgaDocument as Organization
from models.notification import notifications
from models.contract import contracts
from models.project import projects
from models.clients import eth_cli

from pymongo import MongoClient
from ethjsonrpc import ParityEthJsonRpc
import scrypt
from rlp.utils import encode_hex

print("INITIALIZING TESTS")
keyDirectory = environ.get('KEYS_DIRECTORY')
for keyFile in listdir(keyDirectory):
	if keyFile.startswith("UTC"):
		remove(path.join(keyDirectory, keyFile))
		print("removed", keyFile)

if "noUser" not in sys.argv:
	users.delete_many({})
if "noOrga" not in sys.argv:
	organizations.delete_many({})
	contracts.delete_many({})
	projects.delete_many({})
notifications.delete_many({})
session = Collection(collection=client.main.sessions)

session.delete_many({})

SALT_LOGIN_PASSWORD = "du gros sel s'il vous plait"

test_user = {
	"name": "basic",
        "firstname": "Thomas",
        "lastname": "Duvent",
        "email": "basic@societhy.fr",
	"password": encode_hex(scrypt.hash("test", SALT_LOGIN_PASSWORD)),
	"account": None,
	"eth": {
		"keys": {}
	}
}

test_miner = {
	"name": "simon",
        "firstname": "Simon",
        "lastname": "Legrand",
        "email": "miner@societhy.fr",
	"password": encode_hex(scrypt.hash("test", SALT_LOGIN_PASSWORD)),
	"account": None,
	"eth": {
		"keys": {}
	}
}

user_martin = {
	"name": "jerem",
        "firstname": "Jeremy",
        "lastname": "Martin",
        "city": "Amien",
        "email": "jeremy.martin@societhy.fr",
	"password": encode_hex(scrypt.hash("test", SALT_LOGIN_PASSWORD)),
	"account": None,
	"eth": {
		"keys": {}
	}
}

anonym_template = {
	"name": "anonym",
        "firstname": "Anonym",
        "lastname": "Anonym",
        "city": "Unknown",
        "email": "anonym@societhy.fr",
	"password": encode_hex(scrypt.hash("test", SALT_LOGIN_PASSWORD)),
	"account": None,
	"eth": {
		"keys": {}
	}
}

test_orga = {
	"name": "Societhy_anonymous_orga",
	"description" : "test_description", 
	"gov_model" : "ngo",
	"rules": {
		"hidden": False,
		"delegated_voting": True,
		"curators": True,
		"quorum" : 50,
		"majority": 50,
		"anonymous": True
	}
}

# InitAll
if "noUser" not in sys.argv:
	test_user_doc = UserDocument(doc=test_user, gen_skel=True, notifs=False)
	miner = UserDocument(doc=test_miner, gen_skel=True, notifs=False)
	user_martin_doc = UserDocument(doc=user_martin, gen_skel=True, notifs=False)
	test_user_doc.save()
	miner.save()
	user_martin_doc.save()
       
	with open(path.join(keyDirectory, 'test_key.key'), 'rb') as f:
		keys.importNewKey(miner, f)
miner = users.find_one({"name": "simon"})
bw.run()



# CREATE USERS
def create_user(number, user):
	i = 0
	user_docs = {}
	while number >= i:
		user["name"] = "anonyme_" + str(i)
		user["firstname"] = "anonyme_" + str(i)
		user["lastname"] = "anonyme_" + str(i)
		user["email"] = "anonyme_" + str(i) + "@societhy.fr"
		print("creating user " + str(i))
		user_docs[i] = UserDocument(doc=user, gen_skel=True, notifs=False)
		user_docs[i].save()                
		addr = keys.genLinkedKey(user_docs[i], "test")
		user.update()              
		miner.unlockAccount(password='simon')
		ret = eth_cli.transfer(miner.get('account'), user_docs[i]["account"], 50000000000000000000000000)
		i = i + 1		 
	return user_docs

# CREATE ORGA
def create_orga(orga, miner, password):
	ret = base_orga.createOrga(miner, password, orga)
	tx_hash = ret.get('data').get('tx_hash')
	bw.waitTx(tx_hash)
	bw.waitBlock()
	return ret
	



        
# CREATE ANONYMOUS USERS
if "noUser" not in sys.argv:
	user_docs = create_user(40, anonym_template)
else:
	user_docs = users.find({"city": "Unknown"})

#   UNICEF
def create_unicef(miner):
	orga_unicef = {
	        "name": "UNICEF", 
	        "description" : "Présent dans 190 pays et territoires, l’UNICEF se bat depuis soixante-dix ans pour les droits de chaque enfant. Découvrez notre action par l’intermédiaire des programmes que nous créons au nom des enfants.", 
	        "gov_model" : "ngo",
	        "initial_funds": 2570,
	        "rules": {
		        "delegated_voting": True,
		        "curators": True,
		"quorum" : 50,
		"majority": 50
	        }
        
        }
	if "noOrga" not in sys.argv:
		create_orga(orga_unicef, miner, "simon")

                
	unicef_doc = organizations.find_one({"name": "UNICEF"})
	print(unicef_doc["_id"])	
	#Join and donate and leave
	x  = 0
	if "noJoin" not in sys.argv:
		for x in range(0, 27):
			print("user " + str(x) + " join unicef orga")
			base_orga.joinOrga(user_docs[x], "test", unicef_doc["_id"])
			bw.waitEvent('NewMember')
			user_docs[x].reload()
			if (randint(0, 100) in range(0, 80)):
				ret = base_orga.donateToOrga(user_docs[x], "test", unicef_doc['_id'], {"amount": randint(500, 1200)})
				bw.waitEvent("DonationMade")
			sleep(1)
			user_docs[x].reload()
			if (randint(0, 100) in range(0, 30)):
				base_orga.leaveOrga(user_docs[x], "test", unicef_doc["_id"])
				bw.waitEvent("MemberLeft")
				sleep(1)
		
		# Donate
		x = 28
		for x in range(28, 39):
			print("user " + str(x) + " donate to unicef")
			ret = base_orga.donateToOrga(user_docs[x], "test", unicef_doc['_id'], {"amount": randint(100, 800)})
			bw.waitEvent("DonationMade")
			sleep(1)
			user_docs[x].reload()
        # Project
	ret = base_orga.createProjectFromOrga(miner, "simon", unicef_doc.get('_id'), {"name": "Support School in  Kurdistan", "description": "This project aims to help a 1st grade classroom at the school in Baharka IDP Camp on the outskirts of Erbil, Kurdistan, Iraq. ", "invited_users": {}, 'campaign':{"amount_to_raise":7800, "duration": 100}})
	bw.waitTx(ret.get('data'))

create_unicef(miner)
