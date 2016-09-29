from flask import Blueprint, render_template
from core import auth

router = Blueprint('user', __name__)

@router.route('/name/')
def profile_page(user):
	# return render_template("profile_template.html")
	return 'Salut'

@router.route('/auth/<user>')
def auth_user(user):
	success = auth.login(user)
	return "Welcome" if success else "Access Denied"