from os import environ

from flask import Flask, render_template, url_for
from flask_mail import Mail

from api.routes.user import router as user_routes
from api.routes.organization import router as orga_routes
from api.routes.project import router as project_routes
from api.routes.fundraise import router as fundraise_routes


from bson.objectid import ObjectId
from core.notifications import *
from models.project import projects, ProjectDocument as Project
from models.organization import organizations, OrgaDocument as Orga


from core import secret_key
from core.utils import UserJSONEncoder
import core.chat as chat

app = Flask(__name__, template_folder='web/static/', static_url_path='', static_folder='web')
app.secret_key = secret_key
app.json_encoder = UserJSONEncoder


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'societhycompany@gmail.com'
app.config['MAIL_PASSWORD'] = 'JDacdcacdc95'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail()
mail.init_app(app)

jinja_options = app.jinja_options.copy()

jinja_options.update(dict(
	block_start_string='<%',
	block_end_string='%>',
	variable_start_string='%%',
	variable_end_string='%%',
	comment_start_string='<#',
	comment_end_string='#>'
))
app.jinja_options = jinja_options


app.register_blueprint(user_routes)
app.register_blueprint(orga_routes)
app.register_blueprint(project_routes)
app.register_blueprint(fundraise_routes)

@app.after_request
def addHeader(response):
	"""
	Add headers to both force latest IE rendering engine or Chrome Frame,
	and also to cache the rendered page for 10 minutes.
	"""
	response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
	response.headers['Cache-Control'] = 'no-cache, no-store'
	response.headers['Pragma'] = 'no-cache'
	return response

@app.route('/')
def helloWorld():
	notifyToOne(organizations.find_one({"_id": ObjectId("58823a62fa25f07ac36d4b71")}), users.find_one({"_id" : ObjectId("5876417fcba72b00a03cf9f4")}), 'newProposition')
	return render_template("index.html")

socketio = chat.socketio
socketio.init_app(app)

if __name__ == '__main__':
	if environ.get('MINING'):
		from core.blockchain_watcher import blockchain_watcher
		blockchain_watcher.run()
	if environ.get('IP'):
		socketio.run(app, host=environ.get('IP'), port=4242, debug=True, use_reloader=(environ.get('MINING') == None))
	else:
		socketio.run(app, host='127.0.0.1', port=80, debug=True, use_reloader=True)
