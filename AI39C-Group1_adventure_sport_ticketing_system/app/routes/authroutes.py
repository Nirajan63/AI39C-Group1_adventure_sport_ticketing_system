from flask import Blueprint
from app.controlers.auth_control import AuthController


class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()

    def register(self):
        self.bp.route("/", methods=["GET", "POST"])(self.controller.login)

        return self.bp
