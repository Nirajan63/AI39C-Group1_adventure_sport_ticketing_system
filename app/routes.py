from flask import Blueprint

bp = Blueprint("app", __name__)

@bp.route("/login")
def login():
    return "Login Page", 200

