from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Configure CORS to allow our frontend origin to communicate
    CORS(app)
    
    # Import and register blueprints (routes modules)
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    return app
