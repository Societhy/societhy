from os import environ

from flask import Flask, render_template, url_for

from api.routes.user import router as user_routes
from api.routes.organization import router as orga_routes
from api.routes.project import router as project_routes
from api.routes.fundraise import router as fundraise_routes

from core import secret_key

app = Flask(__name__, template_folder='static/templates')
app.secret_key = secret_key

app.register_blueprint(user_routes)
app.register_blueprint(orga_routes)
app.register_blueprint(project_routes)
app.register_blueprint(fundraise_routes)

@app.route('/')
def hello_world():
		return render_template("index.html")

if __name__ == '__main__':
		if environ.get('IP'):
			app.run(host=environ.get('IP'), port=4242, debug=True, use_reloader=True)
		else:
			app.run(host='127.0.0.1', port=80, debug=True, use_reloader=True)
