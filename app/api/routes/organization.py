from flask import Blueprint, Response, render_template, request, jsonify, make_response

from core import base_orga

from api import requires_auth, ensure_fields

router = Blueprint('orga', __name__)

@router.route('/createOrga', methods=['POST'])
@requires_auth
def create_orga(user):
	if ensure_fields(['password', 'newOrga'], request.json):
		ret = base_orga.create_orga(user, request.json.get('password'), request.json.get('newOrga'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)

@router.route('/joinOrga', methods=['POST'])
@requires_auth
def join_orga(user):
	if ensure_fields(['password', 'orga_id'], request.json):
		ret = base_orga.join_orga(user, request.json.get('password'), request.json.get('orga_id'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)

@router.route('/getOrgaMemberList/<token>/<orga_id>', methods=['GET'])
def get_orga_member_list(token, orga_id):
	if orga_id:
		ret = base_orga.get_orga_member_list(token, orga_id)
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)

@router.route('/donateToOrga', methods=['POST'])
@requires_auth
def donate_to_orga(user):
	if ensure_fields(['password', 'orga_id', 'donation'], request.json):
		ret = base_orga.donate_to_orga(user, request.json.get('password'), request.json.get('orga_id'), request.json.get('donation'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)

@router.route('/createProjectFromOrga', methods=['POST'])
@requires_auth
def create_project_from_orga(user):
	if ensure_fields(['password', 'orga_id', 'newProject'], request.json):
		ret = base_orga.create_project_from_orga(user, request.json.get('password'), request.json.get('orga_id'), request.json.get('newProject'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)
	
@router.route('/leaveOrga', methods=['POST'])
@requires_auth
def leave_orga(user):
	if ensure_fields(['password', 'orga_id'], request.json):
		ret = base_orga.leave_orga(user, request.json.get('password'), request.json.get('orga_id'))
		return make_response(jsonify(ret.get('data')), ret.get('status'))
	else:
		return make_response("Wrong request format", 400)
