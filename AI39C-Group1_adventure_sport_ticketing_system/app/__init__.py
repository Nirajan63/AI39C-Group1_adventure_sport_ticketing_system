from flask import Flask
from app.routes.authroutes import AuthRoutes


def create_app():
    app = Flask(__name__)
    auth_route = AuthRoutes()
    app.register_blueprint(auth_route.register())
    return app
