from flask import Blueprint, render_template

router = Blueprint('user', __name__)

@router.route('/name')
def profile_page():
	# return render_template("profile_template.html")
	return 'Salut'