from flask import session, request, Response

from models.organization import organizations, OrgaDocument

def create_orga(user, password, newOrga):
	return {
		"data": "",
		"status": 200
	}

def join_orga(user, password, orga_id):
	orga = organizations.find_one({"_id": orga_id})
	return {
		"data": "",
		"status": 200
	}

def get_orga_member_list(token, orga_id):
	orga = organizations.find_one({"_id": orga_id})
	return {
		"data": "",
		"status": 200
	}

def donate_to_orga(user, password, orga_id, donation):
	orga = organizations.find_one({"_id": orga_id})
	return {
		"data": "",
		"status": 200
	}

def create_project_from_orga(user, password, orga_id, newProject):
	orga = organizations.find_one({"_id": orga_id})
	return {
		"data": "",
		"status": 200
	}

def leave_orga(user, password, orga_id):
	orga = organizations.find_one({"_id": orga_id})
	return {
		"data": "",
		"status": 200
	}
