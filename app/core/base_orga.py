from flask import session, request, Response
from bson import objectid, errors

from models.organization import organizations, OrgaDocument

def getOrgaDocument(user, _id=None, name=None):
	orga = None
	if _id:
		try:
			_id = objectid.ObjectId(_id)
		except errors.InvalidId:
			return {"data": "Not a valid ObjectId, it must be a 12-byte input or a 24-character hex string", "status": 400}
		orga = organizations.find_one({"_id": _id})
	elif name:
		orga = list(organizations.find({"name": name}))
		if len(orga) == 1:
			orga = orga[0]
	return {
		"data": orga,
		"status": 200
	}	

def createOrga(user, password, newOrga):
	# first we have to build the smart contract and write it in '/societhy/contracts'
	# then we need to check the dict newOrga if the data is correct
	# then we build the Organization object providing : name of the contract (without '.sol'), the dict with all data, the owner (UserDocument)
		#	orga = Organization(contract='basic_orga', doc=test_orga, owner=miner)
	# then we deploy the contract to the blockchain (providing the user to alert, password for the owner and name of the orga) and check that the transaction hash exists
		#	tx_hash = orga.deploy_contract(from_=user, password=password, args=[orga_name])
		#	if tx_hash is error return error
	# answer is "organization is being created"
	return {
		"data": "tx_hash",
		"status": 200
	}

def joinOrga(user, password, orga_id):
	# first we find the orga
	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	if not orga:
		return {"data": "Organization does not exists", "status": 400}
	# then we call the model's method and wait for the model to be updated
	tx_hash = orga.join(user, password=password)
	return {
		"data": tx_hash,
		"status": 200
	}

def getOrgaMemberList(token, orga_id):
	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	if not orga:
		return {"data": "Organization does not exists", "status": 400}
	member_list = orga.getMemberList()
	return {
		"data": member_list,
		"status": 200
	}

def donateToOrga(user, password, orga_id, donation):
	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	if not orga:
		return {"data": "Organization does not exists", "status": 400}
	donation_amount = donation.get('amount')
	if user.refreshBalance() > donation_amount:
		tx_hash = orga.donate(user, toWei(donation_amount), password=password)
	return {
		"data": tx_hash,
		"status": 200
	}

def createProjectFromOrga(user, password, orga_id, newProject):
	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	return {
		"data": "",
		"status": 200
	}

def leaveOrga(user, password, orga_id):
	orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
	return {
		"data": "",
		"status": 200
	}
