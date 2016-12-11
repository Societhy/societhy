from flask import Blueprint, Response, render_template, request, jsonify, make_response

from core import auth, keys, user_management, wallet

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

#####################
## USER MANAGEMENT ##
#####################

@router.route('/updateUser', methods=['POST'])
@requires_auth
def update(user):
	ret = user_management.update(user, request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/updateSingleUserField', methods=['POST'])
@requires_auth
def update_single_user_fieldd(user):
	ret = user_management.updateUserField(user,request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

####################
## KEY MANAGEMENT ##
####################


@router.route('/genLinkedKey', methods=['POST'])
@requires_auth
def gen_linked_key(user):
	ret = keys.gen_linked_key(user, request.json.get('password'))
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/keyWasGenerated/<address>')
@requires_auth
def key_was_generated(user, address):
	ret = keys.key_was_generated(user, address)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/importNewKey', methods=['POST'])
@requires_auth
def import_new_key(user):
	keyFile = request.files.get("key")
	if keyFile and keyFile.content_type == 'text/plain':
		ret = keys.import_new_key(user, request.files.get("key"))
	else:
		ret = {
			"data": "Bad file type",
			"status": 400
		}
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/exportDeleteKey/<address>')
@requires_auth
def export_and_delete_key(user, address):
	ret = keys.export_key(user, address, delete=True)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/exportKey/<address>')
@requires_auth
def export_key(user, address):
	ret = keys.export_key(user, address)
	return make_response(jsonify(ret.get('data')), ret.get('status'))


####################
##     WALLET     ##
####################

@router.route('/getAllBalances')
@requires_auth
def get_all_balance(user):
	ret = wallet.refresh_all_balances(user)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/getBalance/<address>')
@requires_auth
def get_balance(user, address):
	ret = wallet.refresh_balance(user, address)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/getTxHistory/<address>')
@requires_auth
def get_tx_history(user, address):
	ret = wallet.get_tx_history(user, address)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

####################
##                ##
####################


@router.route('/user/<user>')
@requires_auth
def user_profile(user):
	return Response({"data":"ok"}, 200)
