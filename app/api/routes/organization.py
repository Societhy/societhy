from flask import Blueprint, Response, render_template, request, jsonify, make_response

from core import auth, keys, user_management, wallet
from api import requires_auth

router = Blueprint('orga', __name__)

@router.route('/newUser', methods=['POST'])
def sign_up():
	ret = auth.sign_up(request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))
