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

from models.errors import NotEnoughFunds
from models.clients import db_filesystem
from models.orga_models import *

def joinProject(user, password, project_id, tag="member"):
	"""
	user : user model document that represent the user who made the request
	password : password used to unlock the ethereum account of the user.
	orga_id : id of the orga the user want to join-in.
	rtag : role attribued to the user. Default is regular member.

	This function is called to add an user to an organisation.

	First, the eth. account is unlocked.
	The organisation in retrieved from database.
	The join() method of the orga model document is called to insert this new user in database.
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