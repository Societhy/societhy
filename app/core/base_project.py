"""
This module is fot hangling all the basic project-related requests.
Every function is defined by her own.
"""

from bson import objectid, errors, json_util
import json

from ethjsonrpc.exceptions import BadResponseError
from flask_socketio import emit, send

from core.utils import toWei

from models import users, UserDocument
from bson.objectid import ObjectId

from models.project import projects, ProjectDocument as Project
from models.contract import contracts
from models.notification import NotificationDocument

from models.errors import NotEnoughFunds
from models.clients import db_filesystem
from models.project import *

def getProject(id):
	"""
	id : id of the project to searchself.

	search for a project.
	"""
	# Ajouter le status ouvert-fermé a la recherche
	proj = projects.find_one({'_id': ObjectId(id)})
	if proj is None:
		return {'data': 'This project does not exist', 'status': 400}
	return {'data': proj, 'status': 200}

def getAllProjects():
	"""
	Return all projects from database.
	"""
	projs = list(projects.find({}))
	return {
		'data': projs,
		'status': 200
	}

def joinProject(user, password, project_id, tag="member"):
	"""
	user : user model document that represent the user who made the request
	password : password used to unlock the ethereum account of the user.
	project_id : id of the project the user want to join-in.
	rtag : role attribued to the user. Default is regular member.

	This function is called to add an user to an projectnisation.

	First, the eth. account is unlocked.
	The projectnisation in retrieved from database.
	The join() method of the project model document is called to insert this new user in database.
	A notification is pushed.
	On an error, 400 is returned, on an OK 200 is returned.
	"""
	if not user.unlockAccount(password=password):
		return {"data": "Invalid password!", "status": 400}
	proj = projects.find_one({"_id": objectid.ObjectId(project_id)})
	if not proj:
		return {"data": "Project does not exists", "status": 400}
	try:
		tx_hash = proj.join(user, tag, password=password)
		if tx_hash is False:
			return {"data": "User does not have permission to join project", "status": 400}
	except BadResponseError as e:
		return {"data": str(e), "status": 400}
	return {
		"data": tx_hash,
		"status": 200
	}

def getProjectMemberList(user, project_id):
	"""
	user : UserDoc
	project_id : string for the mongo id
	"""

	proj = projects.find_one({"_id": objectid.ObjectId(project_id)})
	if not proj:
		return {"data": "Project does not exists", "status": 400}
	member_list = proj.getMemberList()
	return {
		"data": member_list,
		"status": 200
	}

def donateToProject(user, password, project_id, donation):
	"""
	user : user who want to give funds to an projectnisation.
	password : used to unlock the wallet of the user.
	project_id : project who will receive the funds.
	donation : amount of the donation.

	Function used to transfert funds from an user to an projectnisation.

	- The user account is unlocked thanks to the password.
	- The projectnisation is retrieved from the database.
	- A check is performed on the user wallet to see if he do have enough funds.
	- The transfert is lauched on the blockchain.
	- error -> 400 ; OK -> 200
	"""

	if not user.unlockAccount(password=password):
		return {"data": "Invalid password!", "status": 400}
	proj = projects.find_one({"_id": objectid.ObjectId(project_id)})
	if not proj:
		return {"data": "Project does not exists", "status": 400}
	donation_amount = float(donation.get('amount'))
	if user.refreshBalance() > donation_amount:
		tx_hash = proj.donate(user, toWei(donation_amount), password=password)
		if tx_hash is False:
			return {"data": "User does not have permission to donate", "status": 400}
	else:
		return {"data": "Not enough funds in your wallet to process donation", "status": 400}
	return {
		"data": tx_hash,
		"status": 200
	}

def leaveProject(user, password, project_id):
	"""
	user : user who want to give funds to an projectnisation.
	password : used to unlock the wallet of the user.
	project_id : id of the project the user want to leave.

	This function is called when an user want to leave an projectnisation.

	- The wallet is unlocked.
	- The leave order is commited on the blockchain.
	- error -> 400 ; OK -> 200
	"""

	if not user.unlockAccount(password=password):
		return {"data": "Invalid password!", "status": 400}

	project_instance = projects.find_one({"_id": objectid.ObjectId(project_id)})
	try:
		tx_hash = project_instance.leave(user, password=password)
		if tx_hash is False:
			return {"data": "User does not have permission to leave", "status": 400}
	except BadResponseError as e:
		return {"data": str(e), "status": 400}
	NotificationDocument.pushNotif({"sender": {"id": objectid.ObjectId(project_id), "type": "project"}, "subject": {"id": objectid.ObjectId(user.get("_id")), "type": "user"}, "category": "MemberLeft"})

	return {
		"data": tx_hash,
		"status": 200
	}
