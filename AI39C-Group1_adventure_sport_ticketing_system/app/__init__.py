from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes.authroutes import AuthRoutes
from app.routes.AuthRoutes_Admin import AdminRoutes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    
    from app.models.database import init_db
    init_db()

    auth_route = AuthRoutes()
    app.register_blueprint(auth_route.register())

    admin_route = AdminRoutes()
    app.register_blueprint(admin_route.register())

    # Add a dummy csrf_token function to prevent UndefinedError in dashboard_Admin.html template
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=lambda: "dummy-csrf-token-12345")
    
    return app