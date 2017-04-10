"""
This module is fot hangling all the basic organisations-related requests.
Every function is defined by her own.
"""

from flask import session, request, Response
from bson import objectid, errors, json_util
import json

from ethjsonrpc.exceptions import BadResponseError
from flask_socketio import emit, send

from core.utils import toWei

from models.organization import organizations, OrgaDocument
from models.notification import notifications, NotificationDocument as notification
from models.errors import NotEnoughFunds
from models.clients import db_filesystem

def getOrgaDocument(user, _id=None, name=None):
	"""
	user : user model document that represent the user who made the request.
	id : ObjectId who represent the organisation.
	name : name of the orga
	You must provide id OR name.

	The function will return a description of the requested organisation and the associated rights.
	"""

	orga = None
	rights = None
	if _id:
		try:
			_id = objectid.ObjectId(_id)
		except errors.InvalidId:
			return {"data": "Not a valid ObjectId, it must be a 12-byte input or a 24-character hex string", "status": 400}
		orga = organizations.find_one({"_id": _id})
		if orga is None:
			return {"data": "Organization does not exist", "status": 400}
	elif name:
		orga = list(organizations.find({"name": name}))
		if len(orga) == 1:
			orga = orga[0]
		elif len(orga) < 1:
			return {"data": "Organization does not exist", "status": 400}
	if user:
		if user.get('account') in orga.get('members'):
			rights = orga.get('members').get(user.get('account')).get('rights')
		else:
			rights = orga.rights.get('default')

	if orga.get('profil_picture'):
		orga["picture"] = ("data:"+ orga["profile_picture"]["profile_picture_type"]+";base64," + json.loads(json_util.dumps(db_filesystem.get(orga["profile_picture"]["profile_picture_id"]).read()))["$binary"])
	return {
		"data": { "orga": orga, "rights": rights},
		"status": 200
	}	

def getAllOrganizations():
	"""
	Return all the registered organisations.
	"""
	orgas = list(organizations.find({}, organizations.public_info))
	return {
		"data": orgas,
		"status": 200
	}	

def createOrga(user, password, newOrga):
	"""
	user : user model document that represent the user who made the request.
	password : password of the user's ethereum wallet. Needed to trigger the action on the blockchain.
	newOrga : define the organisation the user want to create.

	The purpose of this function is to create an new organisation on Sociehty.
	It first unlock the ethereum account of the user who want to create an organisation.
	Then, it instanciate a new organisation model documentation.
	Then, it try to deploy the contract who represent the organisation on the blockchain.
	Status 200 is returned if all is OK, if not 400 is returned.
	"""

	if not user.unlockAccount(password=password):
		return {"data": "Invalid password!", "status": 400}
	newOrga["members"] = {}
	instance = OrgaDocument(doc=newOrga, owner=user.public(), contract='basic_orga', gen_skel=True)
	try:
		tx_hash = instance.deployContract(from_=user, password=password, args=[newOrga.get('name')])
	except BadResponseError as e:
		return {"data": str(e), "status": 400}
	return {
			"data": {"orga": instance, "tx_hash": tx_hash},
			"status": 200
		}

def addOrgaProfilePicture(user, orga_id, pic, pic_type):
	"""
	user : user model document that represent the user who made the request.
	orga_id : id of the organisation the user want to add a profile picture.
	pic : the photo's bytes.
	pic_type : the MIME type of the photo. e.g. : image/jpeg.

	This function insert in the database the new photo of a given organisation.
	Thanks to the GridFS sytem, photos can be inserted in a database without performance loss.
	"""

	_id = db_filesystem.put(pic)
	ret = organizations.update_one({"_id": objectid.ObjectId(orga_id)}, {"$set": {"profile_picture" : {"profile_picture_id" : _id, "profile_picture_type" : pic_type} } } )
	if ret.modified_count <= 1:
		return {"data":"Photo uploade failure, not inserted into database", "status" : 400}
	return {"data":"OK", "status":200}

def addOrgaDocuments(user, orga_id, doc, name, doc_type):
	"""
	user : user model document that represent the user who made the request.
	orga_id : id of the organisation the user want to add documents.
	doc : document bytes
	name : document name
	doc_type : MIME type of the document.

	This function insert in the database documents related to a given organisation.
	Thanks to the GridFS sytem, documents can be inserted in a database without performance loss.
	"""
	_id = db_filesystem.put(doc, doc_type=doc_type, name=name)
	ret = organizations.update_one({"_id": objectid.ObjectId(orga_id)}, {"$addToSet": { "uploaded_documents" : {"doc_id": _id, "doc_type": doc_type, "doc_name":name} } })
	return {"data":"OK", "status":200}

def getOrgaUploadedDocument(user, doc_id, doc_name):
	"""
	user : user model document that represent the user who made the request.
	doc_id : id of the document user want to retrieve.
	do_name : name of the document user want to retrieve.

	This fuction allow user to download a document who has been previously uploaded.
	"""

	gfile = db_filesystem.get(objectid.ObjectId(doc_id))
	rep = Response(gfile, mimetype=gfile.doc_type, direct_passthrough=True)
	rep.headers['Content-Disposition'] = 'attachment; filename="' + doc_name + '"'
	rep.headers['Content-Type'] = "application/force-download"
	return rep

def joinOrga(user, password, orga_id, tag="member"):
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
	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	if not orga:
		return {"data": "Organization does not exists", "status": 400}

	try:
		tx_hash = orga.join(user, tag, password=password)
	except BadResponseError as e:
		return {"data": str(e), "status": 400}
	return {
		"data": tx_hash,
		"status": 200
	}

def getOrgaMemberList(user, orga_id):
	"""
	user : UserDoc
	orga_id : string for the mongo id
	"""

	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	if not orga:
		return {"data": "Organization does not exists", "status": 400}
	member_list = orga.getMemberList()
	return {
		"data": member_list,
		"status": 200
	}

def donateToOrga(user, password, orga_id, donation):
	"""
	user : user who want to give funds to an organisation.
	password : used to unlock the wallet of the user.
	orga_id : orga who will receive the funds.
	donation : amount of the donation.

	Function used to transfert funds from an user to an organisation.

	- The user account is unlocked thanks to the password.
	- The organisation is retrieved from the database.
	- A check is performed on the user wallet to see if he do have enough funds.
	- The transfert is lauched on the blockchain.
	- error -> 400 ; OK -> 200
	"""

	if not user.unlockAccount(password=password):
		return {"data": "Invalid password!", "status": 400}
	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	if not orga:
		return {"data": "Organization does not exists", "status": 400}
	donation_amount = float(donation.get('amount'))
	if user.refreshBalance() > donation_amount:
		tx_hash = orga.donate(user, toWei(donation_amount), password=password)
	else:
		return {"data": "Not enough funds in your wallet to process donation", "status": 400}
	return {
		"data": tx_hash,
		"status": 200
	}

def createProjectFromOrga(user, password, orga_id, newProject):
	"""
	user : user who want to give funds to an organisation.
	password : used to unlock the wallet of the user.
	orga_id : orga who will receive the funds.
	newProject : object that defines the projet user want to create.

	This function is used when an user want to create a project.


	- The wallet is unlocked.
	- The organisation is retrieved in database.
	- The project creations is commited on the blockchain.
	- error -> 400 ; OK -> 200
	"""

	if not user.unlockAccount(password=password):
		return {"data": "Invalid password!", "status": 400}

	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	if not orga:
		return {"data": "Organization does not exists", "status": 400}
	try:
		tx_hash = orga.createProject(user, newProject, password=password)
	except BadResponseError as e:
		return {"data": str(e), "status": 400}
	return {
		"data": tx_hash,
		"status": 200
	}

def leaveOrga(user, password, orga_id):
	"""
	user : user who want to give funds to an organisation.
	password : used to unlock the wallet of the user.
	orga_id : id of the orga the user want to leave.

	This function is called when an user want to leave an organisation.

	- The wallet is unlocked.
	- The leave order is commited on the blockchain.
	- error -> 400 ; OK -> 200
	"""

	if not user.unlockAccount(password=password):
		return {"data": "Invalid password!", "status": 400}
	
	orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	try:
		tx_hash = orga_instance.leave(user, password=password)
	except BadResponseError as e:
		return {"data": str(e), "status": 400}
	notification.pushNotif({"sender": {"id": objectid.ObjectId(orga_id), "type": "orga"}, "subject": {"id": objectid.ObjectId(user.get("_id")), "type": "user"}, "category": "memberLeave"})

	return {
		"data": tx_hash,
		"status": 200
	}

def getHisto(token, orga_id, date):
	data = notification.getHisto(orga_id, date)
	return {
		"data": data,
		"status": 200
	}

