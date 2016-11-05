from flask import Blueprint, Response, render_template, request, jsonify, make_response
from core import auth, eth

from api import requires_auth

router = Blueprint('user', __name__)

####################
## LOG SIGN TOKEN ##
####################


@router.route('/login', methods=['POST'])
def login():
	ret = auth.login(request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/logout')
@requires_auth
def logout(user):
	ret = auth.logout(user)
	return jsonify(ret)

@router.route('/newUser', methods=['POST'])
def sign_up():
	ret = auth.sign_up(request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/checkTokenValidity/<token>')
def check_token_validity(token):
	ret = auth.check_token_validity(token)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/deleteUser/<user>')
@requires_auth
def delete_user(user):
	ret = auth.delete_user(user)
	return make_response(jsonify(ret.get('data')), ret.get('status'))


####################
## KEY MANAGEMENT ##
####################


@router.route('/genLinkedKey')
@requires_auth
def gen_linked_key(user):
	ret = eth.gen_linked_key(user)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/keyWasGenerated/<address>')
@requires_auth
def key_was_generated(user, address):
	ret = eth.key_was_generated(user, address)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/importNewKey', methods=['POST'])
@requires_auth
def import_new_key(user):
	ret = eth.import_new_key(user, request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/exportDeleteKey', methods=['POST'])
@requires_auth
def export_and_delete_key(user)
	ret = eth.export_and_delete_key(user, request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/exportKey', methods=['POST'])
@requires_auth
def export_key(user)
	ret = eth.export_key(user, request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))


####################
##                ##
####################


@router.route('/user/<user>')
@requires_auth
def user_profile(user):
	print(user)
	return Response({"data":"ok"}, 200)
