from flask import Blueprint, Response, render_template, request, jsonify, make_response
from core import auth

from api import requires_auth

router = Blueprint('user', __name__)

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

@router.route('/user/<user>')
@requires_auth
def user_profile(user):
	print(user)
	return Response({"data":"ok"}, 200)