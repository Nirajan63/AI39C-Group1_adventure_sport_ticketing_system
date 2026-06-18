from flask import Blueprint
from App.Controllers.Auth_Admin import AuthController_Admin


class AuthRoutes_Admin:

    def __init__(self):
        self.bp = Blueprint("auth_admin", __name__, url_prefix="/admin")
        self.controller = AuthController_Admin()

    def register(self):
        # Admin authentication routes
        self.bp.route("/login", methods=["GET", "POST"])(self.controller.login_admin)
        self.bp.route("/logout")(self.controller.logout_admin)
        self.bp.route("/change-password", methods=["GET", "POST"])(self.controller.change_password_admin)
        self.bp.route("/dashboard", methods=["GET"])(self.controller.dashboard_admin)

        # Activity CRUD routes
        self.bp.route("/api/activities", methods=["GET", "POST"])(self.controller.api_activities)
        self.bp.route("/api/activities/<activity_id>", methods=["PUT", "DELETE"])(self.controller.api_activity_detail)
        self.bp.route("/api/activities/duplicate", methods=["POST"])(self.controller.api_duplicate_activity)

        # Booking routes
        self.bp.route("/api/bookings", methods=["GET"])(self.controller.api_bookings)
        self.bp.route("/api/bookings/<int:booking_id>", methods=["PUT"])(self.controller.api_booking_detail)

        # Payment routes
        self.bp.route("/api/payments", methods=["GET"])(self.controller.api_payments)
        self.bp.route("/api/payments/verify", methods=["POST"])(self.controller.api_verify_payment)
        self.bp.route("/api/payments/refund", methods=["POST"])(self.controller.api_refund_payment)
        self.bp.route("/api/payments/manual", methods=["POST"])(self.controller.api_manual_payment)

        # User routes
        self.bp.route("/api/users", methods=["GET"])(self.controller.api_users)
        self.bp.route("/api/users/<int:user_id>", methods=["PUT", "DELETE"])(self.controller.api_user_detail)

        # Notification routes
        self.bp.route("/api/notifications", methods=["POST"])(self.controller.api_notifications)

        # Audit logs route
        self.bp.route("/api/audit-logs", methods=["GET"])(self.controller.api_audit_logs)

        return self.bp
