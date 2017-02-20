from flask import Blueprint, Response, render_template, request, jsonify, make_response

from core import auth, keys, user_management, wallet

from api import requires_auth, populate_user

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
	# print("logout", user)
	ret = auth.logout(user)
	return jsonify(ret)

@router.route('/newUser', methods=['POST'])
def signUp():
	ret = auth.signUp(request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/checkTokenValidity/<token>')
@populate_user
def checkTokenValidity(token, user):
	ret = auth.checkTokenValidity(token, user)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/socketid/<socketid>')
@populate_user
def setSocketId(socketid, user):
	ret = auth.setSocketId(socketid, user)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/deleteUser')
@requires_auth
def deleteUser(user):
	ret = auth.deleteUser(user)
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
def updateSingleUserField(user):
	ret = user_management.updateSingleUserField(user,request.json)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/addToContact', methods=['POST'])
@requires_auth
def addToContactList(user):
    ret = user_management.addToContact(user, request.json)
    return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/delFromContact', methods=['POST'])
@requires_auth
def delFromContact(user):
    ret = user_management.delFromContact(user, request.json)
    return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/findUser', methods=['POST'])
def findUser():
	ret = user_management.findUser(request.json)
	return jsonify(ret.get('data')), ret.get('status')

@router.route('/getUserNotif', methods=['GET'])
@requires_auth
def getUserNotif(user):
	ret = user_management.getUserNotif(user)
	return make_response(ret.get('data'), ret.get('status'))


####################
## KEY MANAGEMENT ##
####################


@router.route('/genLinkedKey', methods=['POST'])
@requires_auth
def genLinkedKey(user):
	ret = keys.genLinkedKey(user, request.json.get('password'))
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/keyWasGenerated/<address>')
@requires_auth
def keyWasGenerated(user, address):
	ret = keys.keyWasGenerated(user, address)
	return make_response(ret.get('data'), ret.get('status'))

@router.route('/importNewKey', methods=['POST'])
@requires_auth
def importNewKey(user):
	keyFile = request.files.get("key")
	if keyFile and keyFile.content_type == 'text/plain':
		ret = keys.importNewKey(user, request.files.get("key"))
	else:
		ret = {
			"data": "Bad file type",
			"status": 400
		}
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/exportDeleteKey/<address>')
@requires_auth
def exportDeleteKey(user, address):
	ret = keys.exportKey(user, address, delete=True)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/exportKey/<address>')
@requires_auth
def exportKey(user, address):
	ret = keys.exportKey(user, address)
	return make_response(jsonify(ret.get('data')), ret.get('status'))


####################
##     WALLET     ##
####################

@router.route('/getAllBalances')
@requires_auth
def getAllBalance(user):
	ret = wallet.refreshAllBalances(user)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/getBalance/<address>')
@requires_auth
def getBalance(user, address):
	ret = wallet.refreshBalance(user, address)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/getTxHistory/<address>')
@requires_auth
def getTxHistory(user, address):
	ret = wallet.getTxHistory(user, address)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

####################
##                ##
####################


@router.route('/user/<user>')
@requires_auth
def user_profile(user):
	return Response({"data":"ok"}, 200)
