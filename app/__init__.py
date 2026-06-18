from flask import Flask


def create_app():
    app = Flask(__name__)
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    return app


app = create_app()