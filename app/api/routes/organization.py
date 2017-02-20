from flask import Blueprint, Response, render_template, request, jsonify, make_response

from core import base_orga

from models.organization import organizations
from api import requires_auth, ensure_fields, populate_user

router = Blueprint('orga', __name__)

@router.route('/getOrganization', methods=['POST'])
@populate_user
def getOrgaDocument(user):
	if 'id' in request.json:
		ret = base_orga.getOrgaDocument(user, _id=request.json.get('id'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	elif 'name' in request.json:
		ret = base_orga.getOrgaDocument(user, name=request.json.get('name'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)

@router.route('/getAllOrganizations', methods=['GET'])
def getAllOrganizations():
	ret = base_orga.getAllOrganizations()
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/createOrga', methods=['POST'])
@requires_auth
def createOrga(user):
	if ensure_fields(['password', {'newOrga': ["name"]}], request.json):
		ret = base_orga.createOrga(user, request.json.get('password'), request.json.get('newOrga'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)

@router.route('/addOrgaProfilePicture', methods=['POST'])
@requires_auth
def addOrgaProfilePicture(user):
	orga_id = request.form.get("orga_id")
	pic_type = request.form.get("type")
	pic = request.files.get("pic")
	ret = base_orga.addOrgaProfilePicture(user, orga_id, pic, pic_type)
	#todo : gerer le retour
	return make_response("ok", 200)

@router.route('/addOrgaDocuments', methods=['POST'])
@requires_auth
def addOrgaDocuments(user):
	orga_id = request.form.get("orga_id")
	doc = request.files.get("doc")
	name = request.form.get("name")
	doc_type = request.form.get("type")
	ret = base_orga.addOrgaDocuments(user, orga_id, doc, name, doc_type)
	return make_response("ok", 200)

@router.route('/getOrgaUploadedDocument/<doc_id>/<doc_name>', methods=['GET'])
@requires_auth
def getOrgaUploadedDocument(user, doc_id, doc_name):
	ret = base_orga.getOrgaUploadedDocument(user, doc_id, doc_name)
	return ret

@router.route('/joinOrga', methods=['POST'])
@requires_auth
def joinOrga(user):
	if ensure_fields(['password', 'orga_id'], request.json):
		ret = base_orga.joinOrga(user, request.json.get('password'), request.json.get('orga_id'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)

@router.route('/getOrgaMemberList/<token>/<orga_id>', methods=['GET'])
@populate_user
def getOrgaMemberList(user, token, orga_id):
	if orga_id:
		ret = base_orga.getOrgaMemberList(token, orga_id)
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)

@router.route('/donateToOrga', methods=['POST'])
@requires_auth
def donateToOrga(user):
	if ensure_fields(['password', 'orga_id', 'donation'], request.json):
		ret = base_orga.donateToOrga(user, request.json.get('password'), request.json.get('orga_id'), request.json.get('donation'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)

@router.route('/createProjectFromOrga', methods=['POST'])
@requires_auth
def createProjectFromOrga(user):
	if ensure_fields(['password', 'orga_id', 'newProject'], request.json):
		ret = base_orga.createProjectFromOrga(user, request.json.get('password'), request.json.get('orga_id'), request.json.get('newProject'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)
	
@router.route('/leaveOrga', methods=['POST'])
@requires_auth
def leaveOrga(user):
	if ensure_fields(['password', 'orga_id'], request.json):
		ret = base_orga.leaveOrga(user, request.json.get('password'), request.json.get('orga_id'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)
