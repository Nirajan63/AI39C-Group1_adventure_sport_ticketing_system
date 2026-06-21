"""
Tests for app/controlers/Auth_Admin.py (AuthController_Admin + module helpers).

Covers every function/method:
  log_audit, send_notification, admin_required (decorator),
  login_admin, logout_admin, change_password_admin, dashboard_admin,
  api_activities, api_activity_detail, api_duplicate_activity,
  api_bookings, api_booking_detail, api_payments, api_verify_payment,
  api_refund_payment, api_manual_payment, api_users, api_user_detail,
  api_notifications, api_send_event_email, api_audit_logs,
  api_gallery_list, api_gallery_add, api_gallery_delete.

Strategy: `Database` is instantiated fresh inside admin_required AND inside
almost every method body, so we patch app.controlers.Auth_Admin.Database
with a stub whose fetch_one() side_effect queue supplies, in order: (1) the
decorator's own role/status lookup, then (2) whatever the method body asks
for next. fetch_all()/execute() are configured per-test as needed.
"""
import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from contextlib import ExitStack

from app.controlers import Auth_Admin
from app.controlers.Auth_Admin import AuthController_Admin, log_audit, send_notification

_app = Flask(__name__)
_app.secret_key = "test-secret-key"


class _session:
    """admin_required / is_logged_in read session from both Auth_Admin and
    baseController; keep both in sync."""
    def __init__(self, value):
        self.value = value
        self._stack = ExitStack()

    def __enter__(self):
        self._stack.enter_context(patch("app.controlers.Auth_Admin.session", self.value))
        self._stack.enter_context(patch("app.controlers.baseController.session", self.value))
        return self.value

    def __exit__(self, *exc_info):
        return self._stack.__exit__(*exc_info)


def _admin_db(decorator_role="admin", decorator_status="active", fetch_one_queue=None, fetch_all_queue=None):
    """Build a fake Database() whose fetch_one() answers the admin_required
    decorator's lookup first, then whatever's queued for the method body."""
    db = MagicMock()
    queue = [{"role": decorator_role, "status": decorator_status}] + list(fetch_one_queue or [])
    db.fetch_one.side_effect = queue
    if fetch_all_queue is not None:
        db.fetch_all.side_effect = fetch_all_queue
    return db


def _logged_in_admin_session(user_id=1, role="admin"):
    return _session({"user": {"id": user_id, "username": "admin1", "role": role}})


# ── log_audit ────────────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_log_audit_inserts_and_closes(mock_database_cls):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db

    log_audit(1, "Login", "User #1", "details")

    mock_db.execute.assert_called_once()
    mock_db.close.assert_called_once()


@patch("app.controlers.Auth_Admin.Database")
def test_log_audit_swallows_db_errors(mock_database_cls):
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("db down")
    mock_database_cls.return_value = mock_db

    # Should not raise.
    log_audit(1, "Login", "User #1")
    mock_db.close.assert_called_once()


# ── send_notification ────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_send_notification_inserts_and_closes(mock_database_cls):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db

    send_notification(1, "Title", "Message")

    mock_db.execute.assert_called_once()
    mock_db.close.assert_called_once()


@patch("app.controlers.Auth_Admin.Database")
def test_send_notification_swallows_db_errors(mock_database_cls):
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("db down")
    mock_database_cls.return_value = mock_db

    send_notification(1, "Title", "Message")
    mock_db.close.assert_called_once()


# ── admin_required decorator ─────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
def test_admin_required_redirects_when_not_logged_in(mock_url_for, mock_redirect):
    mock_url_for.return_value = "/admin/login"
    mock_redirect.return_value = "REDIRECT"

    @Auth_Admin.admin_required
    def protected():
        return "OK"

    with _app.test_request_context():
        with _session({}):
            result = protected()

    assert result == "REDIRECT"


@patch("app.controlers.Auth_Admin.flash")
@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
@patch("app.controlers.Auth_Admin.Database")
def test_admin_required_account_not_found_clears_session(mock_database_cls, mock_url_for, mock_redirect, mock_flash):
    mock_db = MagicMock()
    mock_db.fetch_one.return_value = None
    mock_database_cls.return_value = mock_db
    mock_redirect.return_value = "REDIRECT"

    @Auth_Admin.admin_required
    def protected():
        return "OK"

    session_dict = {"user": {"id": 1, "role": "admin"}}
    with _app.test_request_context():
        with _session(session_dict):
            result = protected()

    assert session_dict == {}
    assert result == "REDIRECT"


@patch("app.controlers.Auth_Admin.flash")
@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
@patch("app.controlers.Auth_Admin.Database")
def test_admin_required_suspended_account_redirects(mock_database_cls, mock_url_for, mock_redirect, mock_flash):
    mock_db = MagicMock()
    mock_db.fetch_one.return_value = {"role": "admin", "status": "suspended"}
    mock_database_cls.return_value = mock_db
    mock_redirect.return_value = "REDIRECT"

    @Auth_Admin.admin_required
    def protected():
        return "OK"

    with _app.test_request_context():
        with _session({"user": {"id": 1, "role": "admin"}}):
            result = protected()

    assert result == "REDIRECT"


@patch("app.controlers.Auth_Admin.flash")
@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
@patch("app.controlers.Auth_Admin.Database")
def test_admin_required_non_admin_role_redirects(mock_database_cls, mock_url_for, mock_redirect, mock_flash):
    mock_db = MagicMock()
    mock_db.fetch_one.return_value = {"role": "Adventure Seeker", "status": "active"}
    mock_database_cls.return_value = mock_db
    mock_redirect.return_value = "REDIRECT"

    @Auth_Admin.admin_required
    def protected():
        return "OK"

    with _app.test_request_context():
        with _session({"user": {"id": 1, "role": "Adventure Seeker"}}):
            result = protected()

    assert result == "REDIRECT"


@patch("app.controlers.Auth_Admin.Database")
def test_admin_required_allows_admin_through(mock_database_cls):
    mock_db = MagicMock()
    mock_db.fetch_one.return_value = {"role": "admin", "status": "active"}
    mock_database_cls.return_value = mock_db

    @Auth_Admin.admin_required
    def protected():
        return "OK"

    with _app.test_request_context():
        with _session({"user": {"id": 1, "role": "admin"}}):
            result = protected()

    assert result == "OK"


# ── login_admin ──────────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
def test_login_admin_already_logged_in_admin_redirects_to_dashboard(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context():
        with _session({"user": {"id": 1, "role": "admin"}}):
            controller = AuthController_Admin()
            result = controller.login_admin()

    assert result == "REDIRECT"


@patch("app.controlers.Auth_Admin.render_template", return_value="LOGIN_PAGE")
@patch("app.controlers.Auth_Admin.flash")
def test_login_admin_post_missing_fields(mock_flash, mock_render):
    with _app.test_request_context(method="POST", data={}):
        with _session({}):
            controller = AuthController_Admin()
            result = controller.login_admin()

    mock_flash.assert_called_once()
    assert result == "LOGIN_PAGE"


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
def test_login_admin_post_success(mock_url_for, mock_redirect, mock_log_audit):
    mock_redirect.return_value = "REDIRECT"

    with _app.test_request_context(method="POST", data={"username": "admin1", "password": "correctpw"}):
        with _session({}):
            controller = AuthController_Admin()
            with patch.object(controller.user_model, "find_by") as mock_find_by:
                user_data = {
                    "id": 1, "username": "admin1", "email": "admin@example.com",
                    "role": "admin", "status": "active", "password": "hashed", "must_change_password": 0,
                }
                mock_find_by.return_value = user_data
                with patch("app.models.user.User.from_db") as mock_from_db:
                    fake_user = MagicMock()
                    fake_user.check_password.return_value = True
                    mock_from_db.return_value = fake_user
                    result = controller.login_admin()

    assert result == "REDIRECT"
    mock_log_audit.assert_called_once()


@patch("app.controlers.Auth_Admin.render_template", return_value="LOGIN_PAGE")
def test_login_admin_post_wrong_password(mock_render):
    with _app.test_request_context(method="POST", data={"username": "admin1", "password": "wrong"}):
        with _session({}):
            controller = AuthController_Admin()
            with patch.object(controller.user_model, "find_by") as mock_find_by:
                mock_find_by.return_value = {"id": 1, "username": "admin1", "role": "admin", "password": "hashed"}
                with patch("app.models.user.User.from_db") as mock_from_db:
                    fake_user = MagicMock()
                    fake_user.check_password.return_value = False
                    mock_from_db.return_value = fake_user
                    result = controller.login_admin()

    assert result == "LOGIN_PAGE"


@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
@patch("app.controlers.Auth_Admin.log_audit")
def test_login_admin_post_must_change_password_redirects(mock_log_audit, mock_url_for, mock_redirect):
    mock_redirect.return_value = "FORCE_CHANGE_REDIRECT"

    with _app.test_request_context(method="POST", data={"username": "admin1", "password": "correctpw"}):
        with _session({}) as sess:
            controller = AuthController_Admin()
            with patch.object(controller.user_model, "find_by") as mock_find_by:
                user_data = {
                    "id": 1, "username": "admin1", "email": "admin@example.com",
                    "role": "admin", "status": "active", "password": "hashed", "must_change_password": 1,
                }
                mock_find_by.return_value = user_data
                with patch("app.models.user.User.from_db") as mock_from_db:
                    fake_user = MagicMock()
                    fake_user.check_password.return_value = True
                    mock_from_db.return_value = fake_user
                    result = controller.login_admin()

    assert result == "FORCE_CHANGE_REDIRECT"
    assert sess.get("force_pw_change") is True


# ── logout_admin ─────────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
def test_logout_admin_clears_session_and_logs_audit(mock_url_for, mock_redirect, mock_log_audit):
    mock_redirect.return_value = "REDIRECT"
    session_dict = {"user": {"id": 1, "role": "admin"}}

    with _app.test_request_context():
        with _session(session_dict):
            controller = AuthController_Admin()
            result = controller.logout_admin()

    assert session_dict == {}
    mock_log_audit.assert_called_once()
    assert result == "REDIRECT"


# ── change_password_admin ───────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
def test_change_password_admin_redirects_when_not_logged_in(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context():
        with _session({}):
            controller = AuthController_Admin()
            result = controller.change_password_admin()

    assert result == "REDIRECT"


@patch("app.controlers.Auth_Admin.render_template", return_value="CHANGE_PW_PAGE")
def test_change_password_admin_post_too_short(mock_render):
    with _app.test_request_context(method="POST", data={"new_password": "short", "confirm_password": "short"}):
        with _session({"user": {"id": 1, "role": "admin"}}):
            controller = AuthController_Admin()
            result = controller.change_password_admin()

    assert result == "CHANGE_PW_PAGE"


@patch("app.controlers.Auth_Admin.render_template", return_value="CHANGE_PW_PAGE")
def test_change_password_admin_post_rejects_default_password(mock_render):
    with _app.test_request_context(method="POST", data={"new_password": "admin123", "confirm_password": "admin123"}):
        with _session({"user": {"id": 1, "role": "admin"}}):
            controller = AuthController_Admin()
            result = controller.change_password_admin()

    assert result == "CHANGE_PW_PAGE"


@patch("app.controlers.Auth_Admin.render_template", return_value="CHANGE_PW_PAGE")
def test_change_password_admin_post_mismatched_passwords(mock_render):
    with _app.test_request_context(
        method="POST", data={"new_password": "newpassword1", "confirm_password": "different1"}
    ):
        with _session({"user": {"id": 1, "role": "admin"}}):
            controller = AuthController_Admin()
            result = controller.change_password_admin()

    assert result == "CHANGE_PW_PAGE"


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.redirect")
@patch("app.controlers.Auth_Admin.url_for")
@patch("app.controlers.Auth_Admin.Database")
def test_change_password_admin_post_success(mock_database_cls, mock_url_for, mock_redirect, mock_log_audit):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db
    mock_redirect.return_value = "REDIRECT"

    session_dict = {"user": {"id": 1, "role": "admin"}, "force_pw_change": True}
    with _app.test_request_context(
        method="POST", data={"new_password": "newpassword1", "confirm_password": "newpassword1"}
    ):
        with _session(session_dict):
            controller = AuthController_Admin()
            result = controller.change_password_admin()

    mock_db.execute.assert_called_once()
    assert "force_pw_change" not in session_dict
    mock_log_audit.assert_called_once()
    assert result == "REDIRECT"


# ── dashboard_admin ──────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.render_template", return_value="DASHBOARD")
@patch("app.controlers.Auth_Admin.Database")
def test_dashboard_admin_renders_stats(mock_database_cls, mock_render):
    mock_db = _admin_db(
        fetch_one_queue=[
            {"total": 10}, {"total": 5}, {"total": 20}, {"total": 8},
            {"total": 3}, {"total": 1}, {"total": 50000}, {"total": 5000}, {"total": 2},
        ],
        fetch_all_queue=[[]],
    )
    mock_database_cls.return_value = mock_db

    with _app.test_request_context():
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            result = controller.dashboard_admin()

    assert result == "DASHBOARD"


# ── api_activities ───────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_activities_get_returns_list(mock_database_cls):
    mock_db = _admin_db(fetch_all_queue=[[{"id": "paragliding"}]])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="GET"):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_activities()

    assert response.json == [{"id": "paragliding"}]


@patch("app.controlers.Auth_Admin.Database")
def test_api_activities_post_as_staff_returns_403(mock_database_cls):
    mock_db = _admin_db(decorator_role="staff")
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"id": "x", "name": "X"}):
        with _logged_in_admin_session(role="staff"):
            controller = AuthController_Admin()
            response, status = controller.api_activities()

    assert status == 403


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.Database")
def test_api_activities_post_creates_activity(mock_database_cls, mock_log_audit):
    mock_db = _admin_db(fetch_one_queue=[None])  # "exists" check -> not found
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"id": "new-act", "name": "New Activity"}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_activities()

    assert response.json["success"] is True


@patch("app.controlers.Auth_Admin.Database")
def test_api_activities_post_missing_required_fields_returns_400(mock_database_cls):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"id": "", "name": ""}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_activities()

    assert status == 400


@patch("app.controlers.Auth_Admin.Database")
def test_api_activities_post_duplicate_id_returns_400(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[{"id": "existing"}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"id": "existing", "name": "X"}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_activities()

    assert status == 400


# ── api_activity_detail ──────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_activity_detail_staff_forbidden(mock_database_cls):
    mock_db = _admin_db(decorator_role="staff")
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={"name": "X"}):
        with _logged_in_admin_session(role="staff"):
            controller = AuthController_Admin()
            response, status = controller.api_activity_detail("paragliding")

    assert status == 403


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.Database")
def test_api_activity_detail_put_updates_activity(mock_database_cls, mock_log_audit):
    mock_db = _admin_db(fetch_one_queue=[{"price": 4500.0}])
    mock_db.fetch_all.return_value.fetchall.return_value = []
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={"name": "Paragliding Updated", "price": 5000}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_activity_detail("paragliding")

    assert response.json["success"] is True


@patch("app.controlers.Auth_Admin.Database")
def test_api_activity_detail_put_missing_name_returns_400(mock_database_cls):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={"name": ""}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_activity_detail("paragliding")

    assert status == 400


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.Database")
def test_api_activity_detail_delete_archives_activity(mock_database_cls, mock_log_audit):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="DELETE"):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_activity_detail("paragliding")

    assert response.json["success"] is True
    mock_log_audit.assert_called_once()


# ── api_duplicate_activity ───────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_duplicate_activity_staff_forbidden(mock_database_cls):
    mock_db = _admin_db(decorator_role="staff")
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={}):
        with _logged_in_admin_session(role="staff"):
            controller = AuthController_Admin()
            response, status = controller.api_duplicate_activity()

    assert status == 403


@patch("app.controlers.Auth_Admin.Database")
def test_api_duplicate_activity_missing_params_returns_400(mock_database_cls):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"source_id": "paragliding"}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_duplicate_activity()

    assert status == 400


@patch("app.controlers.Auth_Admin.Database")
def test_api_duplicate_activity_source_not_found_returns_404(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[None])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(
        method="POST", json={"source_id": "missing", "new_id": "x", "new_name": "X"}
    ):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_duplicate_activity()

    assert status == 404


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.Database")
def test_api_duplicate_activity_success(mock_database_cls, mock_log_audit):
    source = {
        "description": "d", "category": "c", "price": 100, "duration": "1h",
        "capacity": 10, "img": "i.png", "pic": "p.jpg", "location": "l", "difficulty": "Easy",
        "available_dates": "",
    }
    mock_db = _admin_db(fetch_one_queue=[source, None])  # source found, new_id available
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(
        method="POST", json={"source_id": "paragliding", "new_id": "paragliding2", "new_name": "Paragliding 2"}
    ):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_duplicate_activity()

    assert response.json["success"] is True


# ── api_bookings ─────────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_bookings_returns_joined_list(mock_database_cls):
    mock_db = _admin_db(fetch_all_queue=[[{"id": 1, "user_name": "alice"}]])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context():
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_bookings()

    assert response.json == [{"id": 1, "user_name": "alice"}]


# ── api_booking_detail ───────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_booking_detail_not_found_returns_404(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[None])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_booking_detail(99)

    assert status == 404


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.send_notification")
@patch("app.controlers.Auth_Admin.Database")
def test_api_booking_detail_put_updates_booking(mock_database_cls, mock_send_notification, mock_log_audit):
    booking = {
        "id": 5, "status": "confirmed", "payment_status": "pending", "internal_notes": "",
        "date": "2026-07-01", "people": 2, "price": 4500.0, "activity": "Paragliding", "user_id": 1,
    }
    mock_db = _admin_db(fetch_one_queue=[booking])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(
        method="PUT", json={"status": "confirmed", "payment_status": "confirmed", "people": 2, "price": 4500.0}
    ):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_booking_detail(5)

    assert response.json["success"] is True
    mock_send_notification.assert_called_once()


@patch("app.controlers.Auth_Admin.Database")
def test_api_booking_detail_locks_price_for_confirmed_payment(mock_database_cls):
    booking = {
        "id": 5, "status": "confirmed", "payment_status": "confirmed", "internal_notes": "",
        "date": "2026-07-01", "people": 2, "price": 4500.0, "activity": "Paragliding", "user_id": 1,
    }
    mock_db = _admin_db(fetch_one_queue=[booking])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={"price": 9999.0}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_booking_detail(5)

    assert status == 400
    assert "locked" in response.json["message"]


@patch("app.controlers.Auth_Admin.Database")
def test_api_booking_detail_staff_cannot_refund(mock_database_cls):
    booking = {
        "id": 5, "status": "confirmed", "payment_status": "pending", "internal_notes": "",
        "date": "2026-07-01", "people": 2, "price": 4500.0, "activity": "Paragliding", "user_id": 1,
    }
    mock_db = _admin_db(decorator_role="staff", fetch_one_queue=[booking])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={"payment_status": "refunded"}):
        with _logged_in_admin_session(role="staff"):
            controller = AuthController_Admin()
            response, status = controller.api_booking_detail(5)

    assert status == 403


# ── api_payments ─────────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_payments_returns_list(mock_database_cls):
    mock_db = _admin_db(fetch_all_queue=[[{"booking_id": 1}]])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context():
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_payments()

    assert response.json == [{"booking_id": 1}]


# ── api_verify_payment ───────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_verify_payment_missing_booking_id_returns_400(mock_database_cls):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_verify_payment()

    assert status == 400


@patch("app.controlers.Auth_Admin.Database")
def test_api_verify_payment_not_found_returns_404(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[None])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"booking_id": 99}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_verify_payment()

    assert status == 404


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.send_notification")
@patch("app.controlers.Auth_Admin.Database")
def test_api_verify_payment_success(mock_database_cls, mock_send_notification, mock_log_audit):
    mock_db = _admin_db(fetch_one_queue=[{"id": 5, "user_id": 1}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"booking_id": 5}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_verify_payment()

    assert response.json["success"] is True
    mock_send_notification.assert_called_once()


# ── api_refund_payment ───────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_refund_payment_staff_forbidden(mock_database_cls):
    mock_db = _admin_db(decorator_role="staff")
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"booking_id": 5}):
        with _logged_in_admin_session(role="staff"):
            controller = AuthController_Admin()
            response, status = controller.api_refund_payment()

    assert status == 403


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.send_notification")
@patch("app.controlers.Auth_Admin.Database")
def test_api_refund_payment_success(mock_database_cls, mock_send_notification, mock_log_audit):
    mock_db = _admin_db(fetch_one_queue=[{"id": 5, "user_id": 1, "total": 4500.0}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"booking_id": 5}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_refund_payment()

    assert response.json["success"] is True


# ── api_manual_payment ───────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_manual_payment_missing_booking_id_returns_400(mock_database_cls):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_manual_payment()

    assert status == 400


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.send_notification")
@patch("app.controlers.Auth_Admin.Database")
def test_api_manual_payment_success(mock_database_cls, mock_send_notification, mock_log_audit):
    mock_db = _admin_db(fetch_one_queue=[{"id": 5, "user_id": 1}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={"booking_id": 5, "method": "Cash"}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_manual_payment()

    assert response.json["success"] is True


# ── api_users ────────────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_users_returns_list(mock_database_cls):
    mock_db = _admin_db(fetch_all_queue=[[{"id": 1, "name": "alice"}]])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context():
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_users()

    assert response.json == [{"id": 1, "name": "alice"}]


# ── api_user_detail ──────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_user_detail_staff_forbidden(mock_database_cls):
    mock_db = _admin_db(decorator_role="staff")
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={}):
        with _logged_in_admin_session(role="staff"):
            controller = AuthController_Admin()
            response, status = controller.api_user_detail(2)

    assert status == 403


@patch("app.controlers.Auth_Admin.Database")
def test_api_user_detail_not_found_returns_404(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[None])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_user_detail(99)

    assert status == 404


@patch("app.controlers.Auth_Admin.Database")
def test_api_user_detail_self_suspend_prohibited(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[{"id": 1, "role": "admin"}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={"status": "suspended", "role": "admin"}):
        with _logged_in_admin_session(user_id=1):
            controller = AuthController_Admin()
            response, status = controller.api_user_detail(1)

    assert status == 400


@patch("app.controlers.Auth_Admin.Database")
def test_api_user_detail_non_super_admin_cannot_assign_admin_role(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[{"id": 2, "role": "Adventure Seeker"}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={"role": "admin", "status": "active"}):
        with _logged_in_admin_session(user_id=1, role="admin"):
            controller = AuthController_Admin()
            response, status = controller.api_user_detail(2)

    assert status == 403


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.Database")
def test_api_user_detail_put_success(mock_database_cls, mock_log_audit):
    mock_db = _admin_db(fetch_one_queue=[
        {"id": 2, "role": "Adventure Seeker"},  # initial role check
        {"name": "bob", "email": "bob@example.com", "role": "Adventure Seeker", "status": "active"},  # existing
    ])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="PUT", json={"role": "Adventure Seeker", "status": "active"}):
        with _logged_in_admin_session(user_id=1, role="super_admin"):
            controller = AuthController_Admin()
            response = controller.api_user_detail(2)

    assert response.json["success"] is True


@patch("app.controlers.Auth_Admin.Database")
def test_api_user_detail_delete_non_super_admin_forbidden(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[{"id": 2, "role": "Adventure Seeker"}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="DELETE"):
        with _logged_in_admin_session(user_id=1, role="admin"):
            controller = AuthController_Admin()
            response, status = controller.api_user_detail(2)

    assert status == 403


@patch("app.controlers.Auth_Admin.Database")
def test_api_user_detail_delete_self_prohibited(mock_database_cls):
    mock_db = _admin_db(decorator_role="super_admin", fetch_one_queue=[{"id": 1, "role": "super_admin"}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="DELETE"):
        with _logged_in_admin_session(user_id=1, role="super_admin"):
            controller = AuthController_Admin()
            response, status = controller.api_user_detail(1)

    assert status == 400


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.Database")
def test_api_user_detail_delete_success(mock_database_cls, mock_log_audit):
    mock_db = _admin_db(decorator_role="super_admin", fetch_one_queue=[{"id": 2, "role": "Adventure Seeker"}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="DELETE"):
        with _logged_in_admin_session(user_id=1, role="super_admin"):
            controller = AuthController_Admin()
            response = controller.api_user_detail(2)

    assert response.json["success"] is True


# ── api_notifications ────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_notifications_missing_fields_returns_400(mock_database_cls):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_notifications()

    assert status == 400


@patch("app.controlers.Auth_Admin.Database")
def test_api_notifications_title_too_long_returns_400(mock_database_cls):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(
        method="POST", json={"user_id": 1, "title": "x" * 121, "message": "hi"}
    ):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_notifications()

    assert status == 400


@patch("app.controlers.Auth_Admin.Database")
def test_api_notifications_target_not_found_returns_404(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[None])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(
        method="POST", json={"target_id": 99, "title": "Hi", "message": "msg"}
    ):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_notifications()

    assert status == 404


@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.send_notification")
@patch("app.controlers.Auth_Admin.Database")
def test_api_notifications_success(mock_database_cls, mock_send_notification, mock_log_audit):
    mock_db = _admin_db(fetch_one_queue=[{"id": 1}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(
        method="POST", json={"target_id": 1, "title": "Hi", "message": "msg"}
    ):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_notifications()

    assert response.json["success"] is True
    mock_send_notification.assert_called_once()


# ── api_send_event_email ─────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_send_event_email_missing_fields_returns_400(mock_database_cls):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", json={}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_send_event_email()

    assert status == 400


@patch("app.controlers.Auth_Admin.get_db_connection")
@patch("app.controlers.Auth_Admin.Database")
def test_api_send_event_email_no_users_returns_404(mock_database_cls, mock_get_db):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    with _app.test_request_context(
        method="POST", json={"activity_name": "Paragliding", "subject": "Hi", "message": "msg"}
    ):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_send_event_email()

    assert status == 404


@patch("app.controlers.Auth_Admin.send_email", create=True)
@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.get_db_connection")
@patch("app.controlers.Auth_Admin.Database")
def test_api_send_event_email_success(mock_database_cls, mock_get_db, mock_log_audit, mock_send_email):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1, "email": "alice@example.com", "username": "alice"}]
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    with _app.test_request_context(
        method="POST", json={"activity_name": "Paragliding", "subject": "Hi", "message": "msg"}
    ):
        with _logged_in_admin_session():
            with patch("app.utils.email.send_email", return_value=True):
                controller = AuthController_Admin()
                response = controller.api_send_event_email()

    assert response.json["success"] is True
    mock_conn.commit.assert_called_once()


# ── api_audit_logs ───────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_audit_logs_returns_list(mock_database_cls):
    mock_db = _admin_db(fetch_all_queue=[[{"id": 1, "action": "Login"}]])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context():
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_audit_logs()

    assert response.json == [{"id": 1, "action": "Login"}]


# ── api_gallery_list ─────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_gallery_list_returns_posts(mock_database_cls):
    mock_db = _admin_db(fetch_all_queue=[[{"id": 1, "title": "Sunrise", "created_at": None}]])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context():
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_gallery_list()

    assert response.json == [{"id": 1, "title": "Sunrise", "created_at": None}]


@patch("app.controlers.Auth_Admin.Database")
def test_api_gallery_list_db_error_returns_500(mock_database_cls):
    mock_db = MagicMock()
    mock_db.fetch_one.side_effect = [{"role": "admin", "status": "active"}]
    mock_db.fetch_all.side_effect = Exception("db down")
    mock_database_cls.return_value = mock_db

    with _app.test_request_context():
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_gallery_list()

    assert status == 500


# ── api_gallery_add ──────────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_gallery_add_missing_image_returns_400(mock_database_cls):
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST", data={"title": "Test"}):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_gallery_add()

    assert status == 400


@patch("os.makedirs")
@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.Database")
def test_api_gallery_add_success(mock_database_cls, mock_log_audit, mock_makedirs):
    import io
    mock_db = _admin_db()
    mock_database_cls.return_value = mock_db

    data = {
        "title": "Test",
        "description": "desc",
        "image": (io.BytesIO(b"fake image bytes"), "photo.jpg"),
    }
    with _app.test_request_context(method="POST", data=data, content_type="multipart/form-data"):
        with _logged_in_admin_session():
            with patch("werkzeug.datastructures.FileStorage.save"):
                controller = AuthController_Admin()
                response = controller.api_gallery_add()

    assert response.json["success"] is True


# ── api_gallery_delete ───────────────────────────────────────────────────
@patch("app.controlers.Auth_Admin.Database")
def test_api_gallery_delete_not_found_returns_404(mock_database_cls):
    mock_db = _admin_db(fetch_one_queue=[None])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST"):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response, status = controller.api_gallery_delete(99)

    assert status == 404


@patch("os.path.exists", return_value=False)
@patch("app.controlers.Auth_Admin.log_audit")
@patch("app.controlers.Auth_Admin.Database")
def test_api_gallery_delete_success(mock_database_cls, mock_log_audit, mock_exists):
    mock_db = _admin_db(fetch_one_queue=[{"id": 1, "image_url": "gallery/x.jpg", "title": "Sunrise"}])
    mock_database_cls.return_value = mock_db

    with _app.test_request_context(method="POST"):
        with _logged_in_admin_session():
            controller = AuthController_Admin()
            response = controller.api_gallery_delete(1)

    assert response.json["success"] is True
