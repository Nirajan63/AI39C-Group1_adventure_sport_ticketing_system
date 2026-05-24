from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes.authroutes import AuthRoutes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    
    from app.models.database import init_db
    init_db()

    auth_route = AuthRoutes()
    app.register_blueprint(auth_route.register())
    
    return app