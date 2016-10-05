from flask import Blueprint, Response, render_template, request, jsonify, make_response
from core import auth

router = Blueprint('user', __name__)

@router.route('/login', methods=['POST'])
def login():
	success = auth.login(request.json)
	return make_response(jsonify(success.get('data')), success.get('status'))

@router.route('/logout')
@auth.requires_auth
def logout():
	success = auth.logout()
	return jsonify(success)

@router.route('/newUser', methods=['POST'])
def sign_up():
	ret = auth.sign_up(json.loads(request.json))
	return jsonify(ret)

@router.route('/deleteUser/<user>')
def delete_user(user):
	ret = auth.delete_user(user)
	return jsonify(ret)

@router.route('/user/<user>')
@auth.requires_auth
def user_profile(user):
	return Response({"data":"ok"}, 200)