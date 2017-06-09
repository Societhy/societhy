from os import environ
from sys import exit
import re
from signal import signal, SIGINT

from flask import Flask, render_template, url_for, request, make_response, jsonify
from eventlet.greenpool import GreenPool

from api import MongoSessionInterface as MongoSessionInterface
from api.routes.user import router as user_routes
from api.routes.organization import router as orga_routes
from api.routes.project import router as project_routes
from api.routes.fundraise import router as fundraise_routes
from api.routes.notifications import router as notif_routes

from core import secret_key
from core.utils import UserJSONEncoder
from core.chat import socketio

from core.notifications import notifyToOne, mail
from models import organizations, users, projects

app = Flask(__name__, template_folder='../web/static/', static_url_path='', static_folder='../web')
app.secret_key = secret_key
app.json_encoder = UserJSONEncoder

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'societhycompany@gmail.com'
app.config['MAIL_PASSWORD'] = 'JDacdcacdc95'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


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

app.session_interface = MongoSessionInterface()
app.register_blueprint(notif_routes)
app.register_blueprint(user_routes)
app.register_blueprint(orga_routes)
app.register_blueprint(project_routes)
app.register_blueprint(fundraise_routes)

mail.init_app(app)
socketio.init_app(app)

workers_pool = GreenPool(size=3)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['Access-Control-Allow-Headers'] = 'Authentification, authentification, Origin, X-Requested-With, Content-Type, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    if (request.headers.get('origin') is not None):
    	response.headers['Access-Control-Allow-Origin'] = request.headers['origin']
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/')
def helloWorld():
	return render_template("index.html")

@app.route('/searchFor/<query>', methods=['GET'])
def searchForAnything(query):
	
	def process_query(collection):
		regex = re.compile("^%s" % query, re.IGNORECASE)
		return list(collection.lookup(regex))

	data = list()
	for results in workers_pool.imap(process_query, (organizations, users, projects)):
		data += results
	return make_response(jsonify(data), 200)

def stopServer(signal, frame):
	if blockchain_watcher.running:
		blockchain_watcher.stopWithSignal(signal, frame)
	app.session_interface.store.remove({})
	socketio.stop()
	exit()
signal(SIGINT, stopServer)


if __name__ == '__main__':
	if environ.get('MINING'):
		from core.blockchain_watcher import blockchain_watcher
		blockchain_watcher.run()
	if environ.get('IP'):
		socketio.run(app, host=environ.get('IP'), port=4242, debug=True, use_reloader=(environ.get('MINING') == None))
	else:
		socketio.run(app, host='127.0.0.1', port=80, debug=True, use_reloader=True)
