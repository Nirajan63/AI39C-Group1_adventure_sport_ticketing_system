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
        # Page Routes
        self.bp.route("/", methods=["GET"])(self.controller.home)
        self.bp.route("/login", methods=["GET", "POST"])(self.controller.login)
        self.bp.route("/register", methods=["GET"])(self.controller.register_page)
        self.bp.route("/logout", methods=["GET"])(self.controller.logout)
        self.bp.route("/dashboard", methods=["GET"])(self.controller.dashboard)
        self.bp.route("/manage", methods=["GET", "POST"])(self.controller.manage)
        self.bp.route("/wishlist", methods=["GET"])(self.controller.wishlist_page)
        self.bp.route("/forgot", methods=["GET", "POST"])(self.controller.forgot_password)

        # API Routes
        self.bp.route("/signup", methods=["POST"])(AuthController.signup)
        self.bp.route("/book", methods=["POST"])(self.controller.book_activity)
        self.bp.route("/cancel-booking", methods=["POST"])(self.controller.cancel_booking)
        self.bp.route("/api/wishlist/toggle", methods=["POST"])(self.controller.toggle_wishlist)
        
        self.bp.route("/api/auth/google-login/send-otp", methods=["POST"])(
            AuthController.google_send_otp
        )
        self.bp.route("/api/auth/google-login/verify-otp", methods=["POST"])(
            AuthController.google_verify_otp
        )

        return self.bp

