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
        self.bp.route("/activity/<activity_id>", methods=["GET"])(self.controller.activity_page)
        self.bp.route("/referral", methods=["GET"])(self.controller.referral_page)

        # Gallery Routes
        self.bp.route("/gallery", methods=["GET"])(self.controller.gallery)
        self.bp.route("/gallery/add", methods=["POST"])(self.controller.gallery_add)
        self.bp.route("/gallery/delete/<int:post_id>", methods=["DELETE"])(self.controller.gallery_delete)

        # Review Routes
        self.bp.route("/reviews", methods=["GET"])(self.controller.reviews)
        self.bp.route("/reviews/add", methods=["POST"])(self.controller.add_review)
        self.bp.route("/reviews/edit/<int:review_id>", methods=["PUT"])(self.controller.edit_review)
        self.bp.route("/reviews/delete/<int:review_id>", methods=["DELETE"])(self.controller.delete_review)

        # API Routes
        self.bp.route("/signup", methods=["POST"])(AuthController.signup)
        self.bp.route("/book", methods=["POST"])(self.controller.book_activity)
        self.bp.route("/cancel-booking", methods=["POST"])(self.controller.cancel_booking)
        self.bp.route("/api/wishlist/toggle", methods=["POST"])(self.controller.toggle_wishlist)
        self.bp.route("/wishlist/toggle", methods=["POST"])(self.controller.toggle_wishlist)
        self.bp.route("/api/search", methods=["GET"])(self.controller.api_search)
        self.bp.route("/read-notification", methods=["POST"])(self.controller.mark_notification_read)
        self.bp.route("/api/notifications", methods=["GET"])(self.controller.api_get_notifications)
        self.bp.route("/api/notifications/read-all", methods=["POST"])(self.controller.mark_all_notifications_read)
        
        self.bp.route("/api/auth/google-login/send-otp", methods=["POST"])(
            AuthController.google_send_otp
        )
        self.bp.route("/api/auth/google-login/verify-otp", methods=["POST"])(
            AuthController.google_verify_otp
        )

        return self.bp