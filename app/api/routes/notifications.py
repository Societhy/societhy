from flask import Blueprint, make_response, jsonify

from core import user_management, notifications

from api import requires_auth
router = Blueprint('notifications', __name__)

@router.route('/getUserUnreadNotification', methods=['GET'])
@requires_auth
def updateSingleUserField(user):
	ret = notifications.getUserUnreadNotification(user)
	return make_response(jsonify(ret.get('data')), ret.get('status'))
