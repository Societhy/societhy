from flask import Flask

from api.routes.user import router as user_routes
from api.routes.organization import router as orga_routes
from api.routes.project import router as project_routes
from api.routes.crowdsale import router as crowdsale_routes

app = Flask(__name__)

app.register_blueprint(user_routes, url_prefix='/user')
app.register_blueprint(orga_routes)
app.register_blueprint(project_routes)
app.register_blueprint(crowdsale_routes)

@app.route('/')
def hello_world():
        return 'Hello, World!'

if __name__ == '__main__':
        app.run(host='127.0.0.1', port=4242, debug=True, use_reloader=False)
        #        app.run(host='10.224.9.117', port=80, debug=True, use_reloader=False)
