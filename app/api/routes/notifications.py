from api import requires_auth
from core import notifications
from flask import Blueprint, make_response, jsonify
router = Blueprint('notifications', __name__)


@router.route('/getUserUnreadNotification', methods=['GET'])
@requires_auth
def updateSingleUserField(user):
	ret = notifications.getUserUnreadNotification(user)
	return make_response(jsonify(ret.get('data')), ret.get('status'))