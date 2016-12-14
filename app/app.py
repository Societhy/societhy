from os import environ

from flask import Flask, render_template, url_for

from api.routes.user import router as user_routes
from api.routes.organization import router as orga_routes
from api.routes.project import router as project_routes
from api.routes.fundraise import router as fundraise_routes

from core import secret_key
from core.utils import UserJSONEncoder

app = Flask(__name__, template_folder='web/static/', static_url_path='', static_folder='web')
app.secret_key = secret_key
app.json_encoder = UserJSONEncoder
app.config["SESSION_COOKIE_HTTPONLY"] = False

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
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/')
def hello_world():
	print(app.url_map)
	return render_template("index.html")

if __name__ == '__main__':
		if environ.get('IP'):
			app.run(host=environ.get('IP'), port=4242, debug=True, use_reloader=True)
		else:
			app.run(host='127.0.0.1', port=80, debug=True, use_reloader=True)
