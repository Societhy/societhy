from flask import Blueprint, make_response, jsonify, request

from core import user_management, notifications

from api import requires_auth
router = Blueprint('notifications', __name__)


@router.route('/getUserUnreadNotification', methods=['GET'])
@requires_auth
def getUserUnreadNotification(user):
	ret = notifications.getUserUnreadNotification(user)
	return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/markNotificationsAsRead', methods=['POST'])
@requires_auth
def markNotificationsAsRead(user):
	ret = notifications.markNotificationsAsRead(user, request.json.get("data"))
	return make_response(jsonify(ret.get('data')), ret.get('status'))
