"""
Ceci est un test de documentation
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
	Ceci est un test de documentation
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
	Ceci est un test de documentation
	"""

	orgas = list(organizations.find({}, organizations.public_info))
	return {
		"data": orgas,
		"status": 200
	}	

def createOrga(user, password, newOrga):
	"""
	Ceci est un test de documentation
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
	Ceci est un test de documentation
	"""

	_id = db_filesystem.put(pic)
	ret = organizations.update_one({"_id": objectid.ObjectId(orga_id)}, {"$set": {"profile_picture" : {"profile_picture_id" : _id, "profile_picture_type" : pic_type} } } )
	if ret.modified_count <= 1:
		return {"data":"Photo uploade failure, not inserted into database", "status" : 400}
	return {"data":"OK", "status":200}

def addOrgaDocuments(user, orga_id, doc, name, doc_type):
	"""
	Ceci est un test de documentation
	"""

	_id = db_filesystem.put(doc, doc_type=doc_type, name=name)
	ret = organizations.update_one({"_id": objectid.ObjectId(orga_id)}, {"$addToSet": { "uploaded_documents" : {"doc_id": _id, "doc_type": doc_type, "doc_name":name} } })
	print("LALALALA " + str(ret.modified_count))
	return {"ok"}

def getOrgaUploadedDocument(user, doc_id, doc_name):
	"""
	Ceci est un test de documentation
	"""

	gfile = db_filesystem.get(objectid.ObjectId(doc_id))
	rep = Response(gfile, mimetype=gfile.doc_type, direct_passthrough=True)
	rep.headers['Content-Disposition'] = 'attachment; filename="' + doc_name + '"'
	rep.headers['Content-Type'] = "application/force-download"
	return rep

def joinOrga(user, password, orga_id, tag="member"):
	if not user.unlockAccount(password=password):
		return {"data": "Invalid password!", "status": 400}
	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	if not orga:
		return {"data": "Organization does not exists", "status": 400}

	try:
		tx_hash = orga.join(user, tag, password=password)
	except BadResponseError as e:
		return {"data": str(e), "status": 400}
	notification.pushNotif({"sender": {"id": objectid.ObjectId(orga_id), "type": "organization"}, "subject": {"id": objectid.ObjectId(user.get("_id")), "type": "user"}, "category": "newMember"})
	return {
		"data": tx_hash,
		"status": 200
	}

def getOrgaMemberList(token, orga_id):
	"""
	Ceci est un test de documentation
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
	Ceci est un test de documentation
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
	Ceci est un test de documentation
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
	Ceci est un test de documentation
	"""

	if not user.unlockAccount(password=password):
		return {"data": "Invalid password!", "status": 400}
	
	orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	try:
		tx_hash = orga_instance.leave(user, password=password)
	except BadResponseError as e:
		return {"data": str(e), "status": 400}
	notification.pushNotif({"sender": {"id": objectid.ObjectId(orga_id), "type": "organization"}, "subject": {"id": objectid.ObjectId(user.get("_id")), "type": "user"}, "category": "memberLeave"})

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

