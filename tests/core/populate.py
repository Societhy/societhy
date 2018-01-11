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

users.delete_many({})
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
	"password": encode_hex(scrypt.hash("simon", SALT_LOGIN_PASSWORD)),
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
	"password": encode_hex(scrypt.hash("simon", SALT_LOGIN_PASSWORD)),
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
        "email": "sillverr@hotmail.fr",
	"password": encode_hex(scrypt.hash("simon", SALT_LOGIN_PASSWORD)),
	"account": None,
	"eth": {
		"keys": {}
	}
}

# InitAll
test_user_doc = UserDocument(doc=test_user, gen_skel=True, notifs=False)
miner = UserDocument(doc=test_miner, gen_skel=True, notifs=False)
martin_doc = UserDocument(doc=user_martin, gen_skel=True, notifs=False)
test_user_doc.save()
miner.save()
martin_doc.save()

with open(path.join(keyDirectory, 'test_key.key'), 'rb') as f:
	keys.importNewKey(miner, f)
miner = users.find_one({"name": "simon"})

with open(path.join(keyDirectory, 'test_key2.key'), 'rb') as f:
	keys.importNewKey(martin_doc, f)
martin_doc = users.find_one({"email": "jeremy.martin@societhy.com"})
print("Miner has", miner.refreshBalance(), "ethers")
bw.run()



# CREATE USERS
def create_user(user, user_names, user_villes, user_addrs):
	i = 0
	user_docs = {}
	while 50 > i:
		user["eth"]["keys"] = {}
		user["name"] = user_names[i]["firstname"]
		user["firstname"] = user_names[i]["firstname"]
		user["lastname"] = user_names[i]["lastname"]
		user["city"] = user_villes[randint(0, (len(user_villes) - 1))]
		user["address"] = user_addrs[i]
		user["email"] = user_names[i]["firstname"] + "." + user_names[i]["lastname"] + "@societhy.fr"
		print("creating user " + str(i))
		user_docs[i] = UserDocument(doc=user, gen_skel=True, notifs=False)
		user_docs[i].save()
		addr = keys.genLinkedKey(user_docs[i], "simon")
		user.update()
		miner.unlockAccount(password='simon')
		ret = eth_cli.transfer(miner.get('account'), user_docs[i]["account"], 50000000000000000000000)
		i = i + 1
	return user_docs

# CREATE ORGA
def create_orga(orga, miner, password):
	ret = base_orga.createOrga(miner, password, orga)
	tx_hash = ret.get('data').get('tx_hash')
	bw.waitTx(tx_hash)
	bw.waitBlock()
	ret = organizations.find_one({"name": orga["name"]})
	return ret

#   UNICEF
def create_unicef(miner, martin_doc):
	orga_unicef = {
	        "name": "UNICEF",
	        "description" : "Présent dans 190 pays et territoires, l’UNICEF se bat depuis soixante-dix ans pour les droits de chaque enfant. Découvrez notre action par l’intermédiaire des programmes que nous créons au nom des enfants.",
	        "gov_model" : "ngo",
			"creation_date": "Jan 11, 2018 00:00",
	        "initial_funds": 25700,
	        "rules": {
		        "delegated_voting": True,
		        "curators": True,
		"quorum" : 50,
		"majority": 50
	        },
			"rights": {
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
		            "create_proposal": False,
		            "create_offer": True,
		            "vote_proposal": True,
		            "recruit": False,
		            "remove_members": False,
		            "sell_token": True,
		            "buy_token": True,
		            "publish_news": True,
		            "edit_rights": False,
		            "edit_jobs": False,
		            "access_administration": True
		        },
		        "default": {
		            "weight": 0,
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

        }

	create_orga(orga_unicef, miner, "simon")
	unicef_doc = organizations.find_one({"name": "UNICEF"})
	miner.reload()
	offre_1 = {
	        'name': 'Offre 1',
	        'client': unicef_doc.get('address'),
	        'contractor': miner.get('account'),
	        "description": "Raw denim you probably haven't heard of them jean shorts Austin. Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui",
	        'initialWithdrawal': 100,
	        'recurrentWithdrawal': 300,
	        'isRecurrent': True,
	        'duration': 10,
	        "type": "investment",
	        'actors': ["Ox87dhdhdhdhd", "0xcou!s796kld00lkdnld", "0xsalutcava98078"]
        }

	offre_2 = {
	        'name': 'Creation de maison au sud du Sudan',
	        'client': unicef_doc.get('address'),
	        'contractor': miner.get('account'),
	        "description": "Collect de Don pour le Sudan du Sud", "description": "Les combats au Sud-Soudan ont déplacé plus de quatre millions de personnes et infligé des difficultés et des souffrances impensables. Lorsque les affrontements ont éclaté à Wau en juin 2016, des milliers de personnes se sont réfugiées à la base des Nations Unies en bordure de la ville et à la cathédrale Saint-Mary. En juin 2017, 48 000 personnes vivaient entre les deux sites, incapables de rentrer chez eux, en s'appuyant sur leurs besoins fondamentaux.",
	        'initialWithdrawal': 8000,
	        'recurrentWithdrawal': 100,
	        'isRecurrent': True,
	        'duration': 10,
	        "type": "investment",
	        'actors': ["Ox87dhdhdhdhd", "0xcou!s796kld00lkdnld", "0xsalutcava98078"],
                "time_left": 8000
        }
	offre_3 = {
	        'name': 'Offre 2',
	        'client': unicef_doc.get('address'),
	        'contractor': miner.get('account'),
	        "description": "Raw denim you probably haven't heard of them jean shorts Austin. Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui",
	        'initialWithdrawal': 10,
	        'recurrentWithdrawal': 200,
	        'isRecurrent': True,
	        'duration': 12,
	        "type": "employment",
	        'actors': ["Ox87dhdhdhdhd", "0xcou!s796kld00lkdnld", "0xsalutcava98078"]
        }
	members = []
        #Join and donate and leave
	print(user_docs[0])
	for x in range(0, 10):
		base_orga.joinOrga(user_docs[x], "simon", unicef_doc["_id"])
		bw.waitEvent('NewMember')
		user_docs[x].reload()
		members.append(user_docs[x])
		if (randint(0, 100) in range(0, 80)):
			ret = base_orga.donateToOrga(user_docs[x], "simon", unicef_doc['_id'], {"amount": randint(500, 1200)})
			print("ret is", ret, user_docs[x].refreshBalance())
			bw.waitEvent("DonationMade")
			user_docs[x].reload()
			unicef_doc.reload()
		if (randint(0, 100) in range(0, 30)):
			base_orga.leaveOrga(user_docs[x], "simon", unicef_doc["_id"])
			bw.waitEvent("MemberLeft")
			user_docs[x].reload()
			unicef_doc.reload()
			members.remove(user_docs[x])
	# Donate
	x = 11
	for x in range(11, 18):
		print("user " + str(x) + " donate to unicef")
		ret = base_orga.donateToOrga(user_docs[x], "simon", unicef_doc['_id'], {"amount": randint(100, 800)})
		bw.waitEvent("DonationMade")
		user_docs[x].reload()
		unicef_doc.reload()
	create_offer(miner, miner, "simon", unicef_doc, offre_1, members)
	create_offer(miner, miner, "simon", unicef_doc, offre_2, members)
	create_offer(miner, miner, "simon", unicef_doc, offre_3, members)

	ret = base_orga.createProjectFromOrga(miner, "simon", unicef_doc.get('_id'), {"name": "Collect de Don pour le Sudan du Sud", "description": "Les combats au Sud-Soudan ont déplacé plus de quatre millions de personnes et infligé des difficultés et des souffrances impensables. Lorsque les affrontements ont éclaté à Wau en juin 2016, des milliers de personnes se sont réfugiées à la base des Nations Unies en bordure de la ville et à la cathédrale Saint-Mary. En juin 2017, 48 000 personnes vivaient entre les deux sites, incapables de rentrer chez eux, en s'appuyant sur leurs besoins fondamentaux.","invited_ users": {}, 'campaign':{"amount_to_raise": 7000, "duration": 30}})
	bw.waitTx(ret.get('data'))
	unicef_doc.reload()
	miner.reload()

def create_msf(miner):
	orga_msf = {
	        "name": "Medecin Sans Frontier",
	        "description" : "Médecins Sans Frontières est une association médicale humanitaire internationale, créée en 1971 à Paris par des médecins et des journalistes. MSF intervient dans des situations d’exception (conflits, épidémies, catastrophes naturelles) et de grande précarité, afin de porter assistance à ceux dont la vie ou la santé est menacée. L’association délivre ses secours en toute indépendance et impartialité et se réserve le droit de s’exprimer publiquement sur les situations dont ses équipes peuvent être témoin.",
	        "gov_model" : "ngo",
	        "initial_funds": 2570,
	        "rules": {
		        "delegated_voting": True,
		        "curators": True,
		"quorum" : 50,
		"majority": 50
	        },
"rights": {
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
		"create_proposal": False,
		"create_offer": True,
		"vote_proposal": True,
		"recruit": False,
		"remove_members": False,
		"sell_token": True,
		"buy_token": True,
		"publish_news": True,
		"edit_rights": False,
		"edit_jobs": False,
		"access_administration": True
	},
	"default": {
		"weight": 0,
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

        }
	create_orga(orga_msf, miner, "simon")
	miner.reload()

	msf_doc = organizations.find_one({"name": "Medecin Sans Frontier"})
	#Join and donate and leave
	x  = 0
	for x in range(0, 10):
		base_orga.joinOrga(user_docs[x], "simon", msf_doc["_id"])
		bw.waitEvent('NewMember')
		user_docs[x].reload()
		if (randint(0, 100) in range(0, 80)):
			ret = base_orga.donateToOrga(user_docs[x], "simon", msf_doc['_id'], {"amount": randint(500, 1200)})
			bw.waitEvent("DonationMade")
			user_docs[x].reload()
			msf_doc.reload()
		if (randint(0, 100) in range(0, 30)):
			base_orga.leaveOrga(user_docs[x], "simon", msf_doc["_id"])
			bw.waitEvent("MemberLeft")
			user_docs[x].reload()
			msf_doc.reload()

	# Donate
	x = 11
	for x in range(18, 25):
		ret = base_orga.donateToOrga(user_docs[x], "simon", msf_doc['_id'], {"amount": randint(100, 800)})
		bw.waitEvent("DonationMade")
		user_docs[x].reload()
		msf_doc.reload()


        # Project
	ret = base_orga.createProjectFromOrga(miner, "simon", msf_doc.get('_id'), {"name": "Collecte de don de Juin", "description": "Ceci represente la collecte de don mensuel de juin.\n Merci à tous pour votre participation.","invited_users": {}, 'campaign':{"amount_to_raise": 7000, "duration": 30}})
	bw.waitTx(ret.get('data'))
	msf_doc.reload()
	miner.reload()
	ret = base_orga.createProjectFromOrga(miner, "simon", msf_doc.get('_id'), {"descrition": "Le projet de MSF de lutte contre le VIH et la tuberculose dans le district d’uThungulu, qui couvre une population de 114 000 personnes, a toujours pour ambition de devenir le premier site sud-africain à atteindre l’objectif ambitieux des 90-90-90 d’ONUSIDA .\n                Le rapport « Inverser la tendance de l’épidémie de VIH et de tuberculose dans la province de KwaZulu-Natal » a présenté l’approche communautaire du projet, qui a permis d’augmenter le nombre de dépistages intégrés du VIH et de la tuberculose, ainsi que l’accès et l’adhérence au traitement du VIH, avec pour objectif d’influencer la future stratégie du gouvernement sud-africain pour atteindre les objectifs de traitement « 90-90-90 » à l’échelon national. En 2016, 56 029 personnes ont été dépistées, 2370 hommes circoncis et 1 573 756 préservatifs ont été distribués.", "name": "Collecte de don pour la lute contre le VIH et la tuberculose dans la province de Kwazulu-Natal en sud-Afrique", "invited_users": {}, 'campaign':{"amount_to_raise": 10000, "duration": 30}})
	bw.waitTx(ret.get('data'))
	msf_doc.reload()
	miner.reload()
	return msf_doc


def create_youtube(miner):
	orga_youtube = {
	        "name": "VoxMaker",
	        "description" : "Il y en a pour tous les goûts sur VoxMakers !\nNous sommes un collectif de créateurs vidéo divers; nos émissions couvrent de nombreux sujets de la culture populaire :\nJeux vidéo, films, technologie, culture geek, musique, etc...",
	        "gov_model" : "entreprise",
	        "initial_funds": 2570,
                "rules": {
	                "accessibility": "public",
                        "quorum": 50,
                        "majority": 50
                },
"rights": {
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
		"create_proposal": False,
		"create_offer": True,
		"vote_proposal": True,
		"recruit": False,
		"remove_members": False,
		"sell_token": True,
		"buy_token": True,
		"publish_news": True,
		"edit_rights": False,
		"edit_jobs": False,
		"access_administration": True
	},
	"default": {
		"weight": 0,
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
				
        }
	create_orga(orga_youtube, miner, "simon")
	youtube_doc = organizations.find_one({"name": "VoxMaker"})
	#Join and donate and leave NOT TO DO IF ENTREPRISE
#	x  = 22
#	for x in range(22, 30):
#		base_orga.joinOrga(user_docs[x], "simon", youtube_doc["_id"], "member")
#		bw.waitEvent('NewMember')
#		sleep(1)
#		user_docs[x].reload()
#		youtube_doc.reload()
#		if (randint(0, 100) in range(0, 30)):
#			base_orga.leaveOrga(user_docs[x], "simon", youtube_doc["_id"])
#			bw.waitEvent("MemberLeft")
#			user_docs[x].reload()
#			youtube_doc.reload()
#
        # Project
	ret = base_orga.createProjectFromOrga(miner, "simon", youtube_doc.get('_id'), {"name": "JAPAN EXPO JUILLET 2017", "description": "Comme tout les ans, le collectif vous attend à la japan expo!!\nMalheuresement très peu de membre habite près de celle-ci, et la Japan refuse de nous aidé financièrement.\nNous nous en remettons donc à vous, nos cher auditeurs, si vous le souhaitez et si sourtout vous le pouvez, vous pouvez nous soutenir financièrement ici même!\nVoici la liste non exhaustive de toutes nos activités:\n	        Samedi:		Rencontre abonnés, Dédicaces, Ventes de goodies et dvd collector\n		Dimanche:	Sketch et annonces inédits + concert live\n À bientôt ~ ",  "invited_users": {}, 'campaign':{"amount_to_raise": 7000, "duration": 30}})
	bw.waitTx(ret.get('data'))
	youtube_doc.reload()
	miner.reload()
	ret = base_orga.createProjectFromOrga(miner, "simon", youtube_doc.get('_id'), {"name": "Foundraise: Projet Film", "description": "Bonjour à tous, comme annoncé dernièrement, le collectif se lance dans la réalisation d'un court métrage.\n Nous allons pour cela avoir encore besoin de votre aide. Cette aide peut se faire de plusieurs façons: En partageant ou en nous soutenant financièrement.\nSi vous le pouvez et si surtout vous le voulez, vous pouvez par cette page nous setenir fiancièrement pour la réalisation de ce projet. Tout l'argent sera directement mis uniquement à disposition du projet (Payement des acteurs, des lieux, des props)\n Merci à tous pour votre soutien et à bientôt!!!", "invited_users": {}, 'campaign':{"amount_to_raise": 10000, "duration": 30}})
	bw.waitTx(ret.get('data'))
	youtube_doc.reload()
	miner.reload()
	return youtube_doc

# CREATE OFFER
def create_offer(admin, miner, password, orga, offer, members):
	ret = base_orga.createOffer(miner, password, orga.get('_id'), offer)
	bw.waitTx(ret.get('data'))
	orga.reload()
	for index, proposal in enumerate([x for x in orga.get('proposals').values() if x.get('status') == 'pending']):
		ret =  base_orga.createProposal(admin, password, orga.get('_id'), proposal.get('offer').get('address'))
		bw.waitTx(ret.get('data'))
		orga.reload()
		new_proposal = orga.get('proposals').get(proposal.get('offer').get('address'))
	NAY = 0
	YEA = 1
	for index, proposal in enumerate([x for x in orga.get('proposals').values() if x.get('status') == 'debating']):
		for member in members:
			ret = base_orga.voteForProposal(member, password, orga.get('_id'), proposal.get('proposal_id'), randint(0,1))
			bw.waitEvent('VoteCounted')
			orga.reload()


def create_allOrgas(miner, orga_template, orga_names, orga_descs, orga_types):
	for x in range(0, 30):
		orga_template["name"] = orga_names[x]
		orga_template["type"] = orga_types[randint(0,3)]
		print(orga_template["type"])
		size = randint(0, 6200)
		orga_template["description"] = orga_descs[size: (size + randint(0, 300))]
		orga_doc = create_orga(orga_template, miner, "simon")

anonym_template = {
	"name": "anonym",
        "firstname": "Anonym",
        "lastname": "Anonym",
        "city": "Unknown",
        "email": "anonym@societhy.fr",
	"password": encode_hex(scrypt.hash("simon", SALT_LOGIN_PASSWORD)),
	"account": None,
	"eth": {
		"keys": {}
	}
}
orga_types = ["ngo", "entreprise", "dao", "public_company"]

user_names = [
{"firstname": "Tina", "lastname": "Johnson"}, {"firstname": "Lillie", "lastname": "Newman"}, {"firstname": "Albert", "lastname": "Gardner"}, {"firstname": "Nancy", "lastname": "Armstrong"}, {"firstname": "Eleanor", "lastname": "Reeves"}, {"firstname": "Marcos", "lastname": "Wolfe"}, {"firstname": "Daryl", "lastname": "Adams"}, {"firstname": "Alicia", "lastname": "Rivera"}, {"firstname": "Hugo", "lastname": "Mckenzie"}, {"firstname": "Ella", "lastname": "Park"}, {"firstname": "Jeremy", "lastname": "Floyd"}, {"firstname": "Jaime", "lastname": "Alvarez"}, {"firstname": "Dewey", "lastname": "Norris"}, {"firstname": "Arnold", "lastname": "Herrera"}, {"firstname": "Mildred", "lastname": "Gross"}, {"firstname": "Verna", "lastname": "Wilkins"}, {"firstname": "Debra", "lastname": "Pearson"}, {"firstname": "Jesus", "lastname": "Perez"}, {"firstname": "Shawna", "lastname": "Powell"}, {"firstname": "Misty", "lastname": "Cannon"}, {"firstname": "Leona", "lastname": "Bryant"}, {"firstname": "Johnnie", "lastname": "Poole"}, {"firstname": "Jackie", "lastname": "Washington"}, {"firstname": "Victor", "lastname": "Bowers"}, {"firstname": "Elmer", "lastname": "Ramirez"}, {"firstname": "Nora", "lastname": "Robbins"}, {"firstname": "Floyd", "lastname": "Simon"}, {"firstname": "Neal", "lastname": "Long"}, {"firstname": "Kerry", "lastname": "Joseph"}, {"firstname": "Cora", "lastname": "Evans"}, {"firstname": "Wilbur", "lastname": "Harris"}, {"firstname": "Camille", "lastname": "Rios"}, {"firstname": "Jodi", "lastname": "Moreno"}, {"firstname": "Lora", "lastname": "Terry"}, {"firstname": "Phil", "lastname": "Delgado"}, {"firstname": "Boyd", "lastname": "Duncan"}, {"firstname": "Steven", "lastname": "Brewer"}, {"firstname": "Janie", "lastname": "Jordan"}, {"firstname": "Oscar", "lastname": "Arnold"}, {"firstname": "Erica", "lastname": "Myers"}, {"firstname": "Anita", "lastname": "Mcdaniel"}, {"firstname": "Richard", "lastname": "Chapman"}, {"firstname": "Everett", "lastname": "Santos"}, {"firstname": "Irving", "lastname": "Hawkins"}, {"firstname": "Courtney", "lastname": "Tran"}, {"firstname": "Ignacio", "lastname": "Hammond"}, {"firstname": "Angelina", "lastname": "Bates"}, {"firstname": "Joann", "lastname": "Mccormick"}, {"firstname": "April", "lastname": "Hardy"}, {"firstname": "Ross", "lastname": "", "lastname": "Schneider"}]

user_villes = ["Paris", "Strasbourg", "LongChamp", "Lyon", "Grenoble", "Marseille", "Rouen", "Avignon", "Poitier", "Angers", "Versailles", "Créteil", "Cannes"]

user_addrs = [
"8026 Rosewood St.","Madison Heights, MI 48071","372 Coffee St.","Elyria, OH 44035","816 Depot St.","Sewell, NJ 08080","766 High Noon Ave.","Muskegon, MI 49441","463 Alton Ave.","Greenville, NC 27834","9630 Lancaster Drive","Long Branch, NJ 07740","9427 Van Dyke Ave.","Naples, FL 34116","9911 E. Woodside Lane","Fresno, CA 93706","4 Laurel Drive","Duluth, GA 30096","75 SE. Rockaway Dr.","Sun City, AZ 85351","117 Railroad Dr.","Amsterdam, NY 12010","7171 Riverview Drive","Flowery Branch, GA 30542","849 Whitemarsh Rd.","Greensburg, PA 15601","8005 Goldfield St.","Loveland, OH 45140","8322 Stillwater Drive","Egg Harbor Township, NJ 08234","333 Trout Ave.","Palm Coast, FL 32137","45 Highland Ave.","Findlay, OH 45840","527 Beach Dr.","Dickson, TN 37055","901 Summerhouse Dr.","South Plainfield, NJ 07080","55 NW. Vernon Drive","Nashville, TN 37205","9759 Morris St.","Cordova, TN 38016","8327 Buckingham Rd.","Camas, WA 98607","504 Schoolhouse Dr.","Anchorage, AK 99504","8185 Acacia Street","Waynesboro, PA 17268","9112 Princess Dr.","North Attleboro, MA 02760","721 Marsh Court","Toms River, NJ 08753","489 River Street","King Of Prussia, PA 19406","340 Mulberry Rd.","Fayetteville, NC 28303","558 Victoria St.","Hartford, CT 06106","8215 South Victoria Drive","Chattanooga, TN 37421","98 Howard Road","Mc Lean, VA 22101","9176 Riverside Dr.","Woodbridge, VA 22191","723 Edgewood St.","Saratoga Springs, NY 12866","556 Thompson St.","Davison, MI 48423","97 S. Sierra Road","Oakland Gardens, NY 11364","946 Bradford Ave.","West Orange, NJ 07052","639 Livingston Dr.","Fort Worth, TX 76110","7874 Foxrun St.","Apt E","Pittsford, NY 14534","8973 North Brewery Drive","Homestead, FL 33030","8821 East Main Drive","Owatonna, MN 55060","65 Golf Drive","Ottawa, IL 61350","961 Cedar Swamp Court","Boston, MA 02127","8399 Princess Drive","Willingboro, NJ 08046","8313 Carson Ave.","Taunton, MA 02780","290 Cambridge St.","Arvada, CO 80003","37 South Sierra St.","Port Washington, NY 11050","50 Jefferson Court","Ottumwa, IA 52501","912 Trout St.","Clarkston, MI 48348","834 W. Union St.","East Lansing, MI 48823","893 South Washington Avenue","Ontario, CA 91762"]

orga_names = ["MonOrga", "La grandeOrga","Paxton","Braxton","Veolia", "Canal +", "EFD", "RATP", "Virgin", "SOCIETHY", "alliance", "alliancego", "goservices", "servicespro", "proeco", "ecotop", "topmy", "mybio", "biomultiservice", "multiserviceservice", "serviceaxe", "axeideal", "idealexpert", "expertconcept", "conceptadvisor", "advisorconsulting", "consultingconsultant", "consultantconsult", "consultconseil", "conseilsolution", "solution team", "teamplus", "pluschrono", "chronoexpress", "expressfrance", "francefocus", "focuscentre", "centrefirst", "first technologie", "technologiecommerce", "commerceassu", "assudeco", "deco transport", "transportexport", "exportbusiness", "business immobilier", "immobilier","great", "plusgreat", "chronogreat", "expressgreat", "francegreat", "focusgreat", "centregreat", "first", "great", "technologiegreat", "commercegreat", "assugreat", "deco", "great", "transportgreat", "exportgreat", "business", "great", "immobiliergreat", "elitegreatabgreatad"]


orga_descs = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam blandit elit mauris, id luctus diam pretium a. Ut mauris velit, elementum et diam id, egestas finibus enim. Suspendisse tincidunt leo quis euismod ornare. Etiam dignissim placerat dictum. Sed rhoncus hendrerit nunc sit amet faucibus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Sed varius arcu ut nulla cursus auctor. Donec posuere dignissim sapien sit amet consequat.\n\nEtiam ultrices neque elit, in feugiat augue posuere vel. Ut in tortor ac mauris ullamcorper feugiat. Vivamus dignissim eros vitae ante ornare, nec fermentum nulla lacinia. Fusce ut leo libero. In interdum consequat justo, quis sodales erat. Nunc purus orci, finibus eget volutpat a, ornare a ipsum. Curabitur sit amet risus a tortor fermentum euismod in a augue. Phasellus est libero, bibendum sit amet eros sed, scelerisque euismod nibh. Integer et efficitur ante. Proin congue pulvinar bibendum. Suspendisse et sollicitudin tortor, id blandit velit. Phasellus eu ante sed massa pulvinar mattis. Nullam mattis diam sit amet nisl posuere rutrum. Nulla ornare ultrices tellus sit amet volutpat.\n\nDonec mattis tincidunt sollicitudin. Sed nec pulvinar dolor. Nam pretium hendrerit augue, ac interdum purus convallis eu. Integer a nibh non libero volutpat luctus ac vel augue. Proin quis volutpat mauris. Sed vel dui viverra, consectetur orci id, congue dui. Pellentesque eu lectus elementum, mattis massa ut, dictum massa. Pellentesque id lorem eu libero finibus vehicula.\n\nVestibulum sodales ullamcorper massa in auctor. Etiam iaculis eleifend lacinia. Fusce aliquam urna eget elit condimentum, tempor tempor ex gravida. Vestibulum quis felis tempor, suscipit lectus non, lobortis justo. Sed at semper mi. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Nunc congue placerat metus eu consectetur. Vivamus molestie arcu pharetra dui lobortis porta. Phasellus sed posuere nisl, vel molestie elit. Phasellus sagittis odio sapien, quis blandit elit interdum vel. Mauris pellentesque eu risus vel rutrum. Nam posuere libero elit, vel suscipit massa varius id. Phasellus in placerat ligula. Aliquam et finibus dolor. Mauris at libero dui.\n\nUt vitae lorem leo. Morbi porta sed justo vel sollicitudin. Pellentesque quis cursus ante. Etiam non libero posuere, dapibus quam sed, suscipit purus. Sed sit amet nulla at lectus vehicula feugiat. Maecenas tempor tortor nec sapien commodo auctor. Vestibulum posuere quam eu libero vehicula lobortis. In non finibus risus. Aenean vehicula nibh vitae ultricies pharetra. Mauris nec felis ligula. Nam condimentum auctor augue a pharetra. Aliquam non tellus a justo dignissim euismod quis a lectus. Nunc vulputate urna ut lorem luctus, quis auctor massa molestie.\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. In faucibus non risus et euismod. Proin ut tempor tortor. Aliquam placerat nunc nulla, quis sollicitudin tortor bibendum at. Cras laoreet vel lacus vitae volutpat. Quisque sit amet libero sollicitudin, posuere dolor efficitur, pharetra nisi. Suspendisse sit amet porttitor diam. Pellentesque imperdiet, erat eu ultrices vehicula, massa magna maximus elit, nec vehicula turpis justo quis massa. Suspendisse ornare non risus id vulputate. Morbi lobortis odio enim, sed vehicula metus pulvinar sit amet. Etiam mattis, massa ut elementum pretium, quam sapien dapibus lorem, quis hendrerit neque mi eu ligula. Nam id suscipit orci. Vivamus congue pellentesque est in condimentum. Suspendisse sollicitudin condimentum ligula vitae mattis. Proin cursus velit vitae nibh malesuada iaculis.\n\nAliquam iaculis tincidunt ultrices. Ut maximus ultricies posuere. Aenean auctor eget libero et varius. Integer semper odio tempus diam malesuada, at finibus felis fermentum. Vestibulum volutpat velit mauris, eu imperdiet turpis rutrum a. Nam tincidunt ac sem non commodo. Ut sed cursus mauris.\n\nUt imperdiet turpis quis sollicitudin dignissim. Pellentesque eget aliquet libero. Curabitur consequat mauris quis felis elementum, at egestas purus accumsan. Aliquam fringilla tortor ut lectus maximus, eu tincidunt libero consequat. Etiam laoreet at dolor eget porta. Vestibulum vel ipsum consectetur, consequat tellus nec, ultrices augue. Mauris bibendum tristique odio sit amet laoreet. Vestibulum vulputate auctor sapien. Praesent bibendum accumsan ipsum, in posuere lorem mollis vitae. Fusce in eleifend justo, eget molestie felis. Suspendisse potenti. Donec eu tempus justo. Ut aliquam risus posuere urna eleifend aliquet. Donec interdum urna et fringilla rutrum. Morbi sagittis ac eros id maximus. Pellentesque et mi in mauris lacinia fringilla.\n\nUt a semper velit. Nunc eget erat pulvinar urna rhoncus lobortis. Vestibulum molestie egestas diam vitae pulvinar. Vestibulum et elit tincidunt, volutpat lorem vitae, porta ex. Mauris ornare leo viverra massa commodo porta. Morbi sollicitudin hendrerit porta. Aenean varius elit non orci hendrerit, quis consectetur erat cursus. Sed placerat dictum odio, eget interdum ipsum aliquam et. Vivamus venenatis vulputate ipsum, sed vestibulum eros sollicitudin nec. Donec sed ornare sapien. Nulla eget tincidunt dolor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer pretium ultricies mauris, vel eleifend massa pharetra nec. Curabitur semper sem nunc, a feugiat nisi luctus vitae. Mauris porta lorem id ullamcorper ullamcorper. Vestibulum at sagittis libero, vel laoreet urna.\n\nAliquam tortor turpis, placerat nec ultrices at, feugiat vitae erat. Aenean sed gravida lacus. Curabitur vel auctor libero. Curabitur quis urna sit amet orci finibus ornare nec ac lacus. Sed iaculis sit amet risus ac mollis. Donec accumsan eros sed lacus efficitur, placerat finibus enim tristique. Phasellus non maximus augue. Sed vitae nisl sed risus ultricies tristique. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Maecenas ornare tortor vehicula eros accumsan eleifend. Curabitur sed turpis bibendum, semper eros non, vulputate diam. Sed ullamcorper purus urna, vel aliquam elit feugiat sit amet. Curabitur nec elit tempor, mattis justo vitae, pulvinar felis."

orga_template = {
	"description" : "test_description",
	"gov_model" : "entreprise",
	"rules": {
		"hidden": False,
		"delegated_voting": True,
		"curators": True,
		"quorum" : 50,
		"majority": 50,
		"anonymous": True
	}
}

# CREATE ANONYMOUS USERS
if "noUser" not in sys.argv:
	user_docs = create_user(anonym_template, user_names, user_villes, user_addrs)
else:
	user_docs = users.find({"city": "Unknown"})


create_unicef(miner, martin_doc)

create_youtube(miner)
create_msf(miner)
create_allOrgas(miner, orga_template, orga_names, orga_descs, orga_types)
