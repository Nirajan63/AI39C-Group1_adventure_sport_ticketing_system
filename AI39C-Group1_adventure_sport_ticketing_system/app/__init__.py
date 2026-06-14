from flask import Flask, session, request, jsonify, abort
from flask_cors import CORS
import secrets
from app.config import Config
from app.routes.authroutes import AuthRoutes
from app.routes.adminroutes import AuthRoutes_Admin
from app.routes.eventroutes import EventRoutes

def generate_csrf_token():
    """Generate or retrieve a per-session CSRF token."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    
    # Enable global Jinja csrf_token function
    app.jinja_env.globals['csrf_token'] = generate_csrf_token
    
    from app.models.database import init_db
    init_db()

    @app.before_request
    def validate_csrf():
        """Block forged cross-site requests on all admin API/state-changing endpoints."""
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return  # Safe methods — no CSRF risk

        # Only enforce on admin API routes
        if not request.path.startswith('/admin/'):
            return

        # Skip the login/logout form itself
        if request.path in ('/admin/login', '/admin/logout'):
            return

        if '_csrf_token' not in session:
            return  # No session — admin_required will reject anyway

        expected = session.get('_csrf_token', '')

        # Accept token from header (AJAX/fetch) or form field
        submitted = (
            request.headers.get('X-CSRF-Token') or
            request.headers.get('X-CSRFToken') or
            (request.form.get('_csrf_token') if request.form else None) or
            (request.json.get('_csrf_token') if request.is_json and request.json else None)
        )

        if not submitted or not secrets.compare_digest(expected, submitted):
            # Return JSON for API calls, HTML redirect for form posts
            if request.is_json or request.path.startswith('/admin/api/'):
                return jsonify({'success': False, 'message': 'Invalid or missing CSRF token'}), 403
            abort(403)

    auth_route = AuthRoutes()
    auth_route.register()
    app.register_blueprint(auth_route.bp)

    admin_route = AuthRoutes_Admin()
    admin_route.register()
    app.register_blueprint(admin_route.bp)

    event_route = EventRoutes()
    event_route.register()
    app.register_blueprint(event_route.bp)

    @app.context_processor
    def inject_user_wishlist():
        user = session.get("user")
        wishlist_ids = []
        if user:
            try:
                from app.models.database import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT activity_id FROM wishlist WHERE user_id = ?", (user["id"],))
                wishlist_ids = [row["activity_id"] for row in cursor.fetchall()]
                conn.close()
            except Exception as e:
                print(f"Error in wishlist context processor: {e}", flush=True)

        return {
            "user_wishlist_ids": wishlist_ids,
        }

    return app