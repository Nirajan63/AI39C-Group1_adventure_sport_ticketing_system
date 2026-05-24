# from flask import Blueprint
# from app.controlers.auth_control import AuthController


# class AuthRoutes:
#     def __init__(self):
#         self.bp = Blueprint("auth", __name__)
#         self.controller = AuthController()

#     def register(self):
#         self.bp.route("/", methods=["GET", "POST"])(self.controller.login)
#         self.bp.route("/manage", methods=["GET", "POST"])(self.controller.manage)
#         return self.bp





from flask import Blueprint
from app.controlers.auth_control import AuthController


class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()

    def register(self):
     self.bp.route("/", methods=["GET", "POST"])(self.controller.register_page)  # ← change login to register_page
     self.bp.route("/manage", methods=["GET", "POST"])(self.controller.manage)

    # YOUR PART - register routes
     self.bp.route("/register", methods=["GET"])(self.controller.register_page)
     self.bp.route("/signup", methods=["POST"])(AuthController.signup)
     self.bp.route("/api/auth/google-login/send-otp", methods=["POST"])(AuthController.google_send_otp)
     self.bp.route("/api/auth/google-login/verify-otp", methods=["POST"])(AuthController.google_verify_otp)

     return self.bp