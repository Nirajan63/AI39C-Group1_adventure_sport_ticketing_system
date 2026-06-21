"""
Tests for app/controlers/auth_control.py (AuthController).

Covers every method:
  home, activity_page, api_search, login, register_page, signup, logout,
  google_send_otp, google_verify_otp, dashboard, cancel_booking,
  book_activity, manage, wishlist_page, toggle_wishlist, forgot_password,
  gallery, gallery_add, gallery_delete, reviews, add_review, edit_review,
  delete_review, mark_notification_read.

get_db_connection is imported at module level in this file
(`from app.models.database import get_db_connection`), so it's patched as
app.controlers.auth_control.get_db_connection throughout.
"""
import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from contextlib import ExitStack

from app.controlers.auth_control import AuthController, otp_store, ACTIVITIES

_app = Flask(__name__)


class _session:
    """is_logged_in()/get_current_user_id() live on BaseController and read
    app.controlers.baseController.session, while AuthController's own
    methods read app.controlers.auth_control.session -- both need patching
    to the same dict so 'logged in' state is consistent everywhere."""
    def __init__(self, value):
        self.value = value
        self._stack = ExitStack()

    def __enter__(self):
        self._stack.enter_context(patch("app.controlers.auth_control.session", self.value))
        self._stack.enter_context(patch("app.controlers.baseController.session", self.value))
        return self.value

    def __exit__(self, *exc_info):
        return self._stack.__exit__(*exc_info)


def _mock_conn():
    """A MagicMock connection/cursor pair where cursor.execute() returns
    the cursor itself, mirroring the real SafeDictCursor chainable API."""
    conn = MagicMock()
    cursor = MagicMock()
    cursor.execute.return_value = cursor
    conn.cursor.return_value = cursor
    return conn, cursor


@pytest.fixture(autouse=True)
def clear_otp_store():
    otp_store.clear()
    yield
    otp_store.clear()


# ── home ─────────────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.render_template")
@patch("app.controlers.auth_control.get_db_connection")
def test_home_logged_in_includes_wishlist(mock_get_db, mock_render):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"count": 3}
    cursor.fetchall.return_value = [{"activity_id": "paragliding"}]
    mock_get_db.return_value = conn
    mock_render.return_value = "RENDERED"

    with _app.test_request_context():
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.home()

    assert result == "RENDERED"
    kwargs = mock_render.call_args[1]
    assert kwargs["wishlist_count"] == 3
    assert kwargs["saved_wishlist"] == ["paragliding"]


@patch("app.controlers.auth_control.render_template")
def test_home_anonymous_user(mock_render):
    mock_render.return_value = "RENDERED"
    with _app.test_request_context():
        with _session({}):
            controller = AuthController()
            result = controller.home()

    kwargs = mock_render.call_args[1]
    assert kwargs["wishlist_count"] == 0
    assert kwargs["saved_wishlist"] == []
    assert result == "RENDERED"


# ── activity_page ────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.render_template")
@patch("app.controlers.auth_control.get_db_connection")
def test_activity_page_static_activity_found(mock_get_db, mock_render):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    mock_get_db.return_value = conn
    mock_render.return_value = "RENDERED"

    with _app.test_request_context():
        with _session({}):
            controller = AuthController()
            result = controller.activity_page("paragliding")

    assert result == "RENDERED"
    kwargs = mock_render.call_args[1]
    assert kwargs["activity"]["name"] == "Paragliding"


@patch("app.controlers.auth_control.flash")
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
@patch("app.controlers.auth_control.get_db_connection")
def test_activity_page_not_found_redirects(mock_get_db, mock_url_for, mock_redirect, mock_flash):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    cursor.execute.return_value.fetchone.return_value = None
    mock_get_db.return_value = conn
    mock_url_for.return_value = "/"
    mock_redirect.return_value = "REDIRECT"

    with _app.test_request_context():
        with _session({}):
            controller = AuthController()
            result = controller.activity_page("totally-unknown-activity")

    mock_flash.assert_called_once()
    assert result == "REDIRECT"


# ── api_search ───────────────────────────────────────────────────────────
def test_api_search_empty_query_returns_empty_list():
    with _app.test_request_context("/api/search?q="):
        controller = AuthController()
        response = controller.api_search()

    assert response.json == []


@patch("app.controlers.auth_control.get_db_connection")
def test_api_search_matches_static_and_db_without_duplicates(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchall.return_value = [
        {"id": "paragliding", "name": "Paragliding", "category": "Adventure", "img": "p.png"},
        {"id": "extra-db-item", "name": "Extra Paraglide Course", "category": "Adventure", "img": "e.png"},
    ]
    mock_get_db.return_value = conn

    with _app.test_request_context("/api/search?q=para"):
        controller = AuthController()
        response = controller.api_search()

    ids = [r["id"] for r in response.json]
    assert "paragliding" in ids
    assert ids.count("paragliding") == 1  # deduped
    assert "extra-db-item" in ids


# ── login ────────────────────────────────────────────────────────────────
def test_login_get_renders_login_page_when_not_logged_in():
    with _app.test_request_context():
        with _session({}):
            with patch("app.controlers.auth_control.render_template", return_value="LOGIN_PAGE") as mock_render:
                controller = AuthController()
                result = controller.login()

    assert result == "LOGIN_PAGE"
    mock_render.assert_called_once_with("login.html")


@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_login_already_logged_in_redirects_to_dashboard(mock_url_for, mock_redirect):
    mock_url_for.return_value = "/dashboard"
    mock_redirect.return_value = "REDIRECT"

    with _app.test_request_context():
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.login()

    mock_url_for.assert_called_once_with("auth.dashboard")
    assert result == "REDIRECT"


@patch("app.controlers.auth_control.get_db_connection")
def test_login_post_json_missing_fields_returns_400(mock_get_db):
    with _app.test_request_context(method="POST", json={"username": ""}):
        with _session({}):
            controller = AuthController()
            response, status = controller.login()

    assert status == 400
    assert response.json["status"] == "error"


@patch("app.controlers.auth_control.get_db_connection")
def test_login_post_json_success(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {
        "id": 1, "username": "alice", "email": "alice@example.com", "password": "secret",
        "first_name": "Alice", "last_name": None, "phone": None, "city": None, "bio": None,
        "language": None, "role": None, "avatar": None, "cover": None, "theme_preference": None,
        "status": "active",
    }
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"username": "alice", "password": "secret"}):
        with _session({}) as sess:
            controller = AuthController()
            response, status = controller.login()

    assert status == 200
    assert response.json["status"] == "success"
    assert sess["user"]["username"] == "alice"


@patch("app.controlers.auth_control.get_db_connection")
def test_login_post_json_wrong_password_returns_400(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"id": 1, "username": "alice", "password": "correct-password"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"username": "alice", "password": "wrong"}):
        with _session({}):
            controller = AuthController()
            response, status = controller.login()

    assert status == 400
    assert response.json["status"] == "error"


@patch("app.controlers.auth_control.get_db_connection")
def test_login_post_json_suspended_account_returns_403(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"id": 1, "username": "alice", "password": "secret", "status": "suspended"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"username": "alice", "password": "secret"}):
        with _session({}):
            controller = AuthController()
            response, status = controller.login()

    assert status == 403
    assert "suspended" in response.json["message"]


@patch("app.controlers.auth_control.render_template")
@patch("app.controlers.auth_control.flash")
@patch("app.controlers.auth_control.get_db_connection")
def test_login_post_form_missing_fields_flashes_and_renders(mock_get_db, mock_flash, mock_render):
    mock_render.return_value = "LOGIN_PAGE"
    with _app.test_request_context(method="POST", data={"username": ""}):
        with _session({}):
            controller = AuthController()
            result = controller.login()

    mock_flash.assert_called_once()
    assert result == "LOGIN_PAGE"


# ── register_page ────────────────────────────────────────────────────────
def test_register_page_renders_when_not_logged_in():
    with _app.test_request_context():
        with _session({}):
            with patch("app.controlers.auth_control.render_template", return_value="REGISTER") as mock_render:
                controller = AuthController()
                result = controller.register_page()

    assert result == "REGISTER"
    mock_render.assert_called_once_with("register.html")


@patch("app.controlers.auth_control.render_template", return_value="REGISTER")
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_register_page_redirects_when_already_logged_in(mock_url_for, mock_redirect, mock_render):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context():
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.register_page()

    assert result == "REDIRECT"


# ── signup ───────────────────────────────────────────────────────────────
def test_signup_missing_body_returns_400():
    with _app.test_request_context(method="POST", json={}):
        response, status = AuthController.signup()

    assert status == 400


def test_signup_missing_fields_returns_400():
    with _app.test_request_context(method="POST", json={"username": "bob"}):
        response, status = AuthController.signup()

    assert status == 400


@patch("app.controlers.auth_control.get_db_connection")
def test_signup_username_taken_returns_400(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"id": 1}
    mock_get_db.return_value = conn

    with _app.test_request_context(
        method="POST", json={"username": "bob", "email": "bob@example.com", "password": "pw"}
    ):
        response, status = AuthController.signup()

    assert status == 400
    assert "Username" in response.json["message"]


@patch("app.controlers.auth_control.get_db_connection")
def test_signup_success_returns_201(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = None  # neither username nor email exists
    mock_get_db.return_value = conn

    with _app.test_request_context(
        method="POST", json={"username": "newbob", "email": "newbob@example.com", "password": "pw"}
    ):
        response, status = AuthController.signup()

    assert status == 201
    assert response.json["status"] == "success"


@patch("app.controlers.auth_control.get_db_connection")
def test_signup_db_error_during_insert_returns_500(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = None
    cursor.execute.side_effect = [cursor, cursor, Exception("insert failed")]
    mock_get_db.return_value = conn

    with _app.test_request_context(
        method="POST", json={"username": "newbob", "email": "newbob@example.com", "password": "pw"}
    ):
        response, status = AuthController.signup()

    assert status == 500
    assert response.json["status"] == "error"


# ── logout ───────────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_logout_clears_session_and_redirects(mock_url_for, mock_redirect):
    mock_url_for.return_value = "/login"
    mock_redirect.return_value = "REDIRECT"
    session_dict = {"user": {"id": 1}}

    with _app.test_request_context():
        with _session(session_dict):
            controller = AuthController()
            result = controller.logout()

    assert session_dict == {}
    mock_url_for.assert_called_once_with("auth.login")
    assert result == "REDIRECT"


# ── google_send_otp ──────────────────────────────────────────────────────
def test_google_send_otp_missing_email_returns_400():
    with _app.test_request_context(method="POST", json={}):
        response, status = AuthController.google_send_otp()

    assert status == 400


@patch("app.controlers.auth_control.send_email", return_value=True)
@patch("builtins.open", new_callable=MagicMock)
def test_google_send_otp_success_stores_code(mock_open, mock_send_email):
    with _app.test_request_context(method="POST", json={"email": "alice@example.com"}):
        response, status = AuthController.google_send_otp()

    assert status == 200
    assert "alice@example.com" in otp_store
    mock_send_email.assert_called_once()


@patch("app.controlers.auth_control.send_email", return_value=False)
@patch("builtins.open", new_callable=MagicMock)
def test_google_send_otp_email_failure_returns_500(mock_open, mock_send_email):
    with _app.test_request_context(method="POST", json={"email": "alice@example.com"}):
        response, status = AuthController.google_send_otp()

    assert status == 500


# ── google_verify_otp ────────────────────────────────────────────────────
def test_google_verify_otp_missing_fields_returns_400():
    with _app.test_request_context(method="POST", json={"email": "a@example.com"}):
        response, status = AuthController.google_verify_otp()

    assert status == 400


def test_google_verify_otp_no_record_returns_400():
    with _app.test_request_context(method="POST", json={"email": "nobody@example.com", "code": "123456"}):
        response, status = AuthController.google_verify_otp()

    assert status == 400


def test_google_verify_otp_expired_code_returns_400():
    import time
    otp_store["a@example.com"] = {"code": "123456", "expires_at": time.time() - 10}

    with _app.test_request_context(method="POST", json={"email": "a@example.com", "code": "123456"}):
        response, status = AuthController.google_verify_otp()

    assert status == 400
    assert "a@example.com" not in otp_store


def test_google_verify_otp_wrong_code_returns_400():
    import time
    otp_store["a@example.com"] = {"code": "123456", "expires_at": time.time() + 100}

    with _app.test_request_context(method="POST", json={"email": "a@example.com", "code": "000000"}):
        response, status = AuthController.google_verify_otp()

    assert status == 400


@patch("app.controlers.auth_control.send_email", return_value=True)
@patch("app.controlers.auth_control.get_db_connection")
def test_google_verify_otp_success_existing_user(mock_get_db, mock_send_email):
    import time
    otp_store["alice@example.com"] = {"code": "123456", "expires_at": time.time() + 100}
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {
        "id": 1, "username": "alice", "email": "alice@example.com", "first_name": None,
        "last_name": None, "phone": None, "city": None, "bio": None, "language": None,
        "role": None, "avatar": None, "cover": None, "theme_preference": None,
    }
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"email": "alice@example.com", "code": "123456"}):
        with _session({}) as sess:
            response, status = AuthController.google_verify_otp()

    assert status == 200
    assert sess["user"]["username"] == "alice"
    assert "alice@example.com" not in otp_store


@patch("app.controlers.auth_control.send_email", return_value=True)
@patch("app.controlers.auth_control.get_db_connection")
def test_google_verify_otp_auto_registers_new_user(mock_get_db, mock_send_email):
    import time
    otp_store["newuser@example.com"] = {"code": "123456", "expires_at": time.time() + 100}
    conn, cursor = _mock_conn()
    new_user_row = {
        "id": 2, "username": "newuser", "email": "newuser@example.com", "first_name": None,
        "last_name": None, "phone": None, "city": None, "bio": None, "language": None,
        "role": None, "avatar": None, "cover": None, "theme_preference": None,
    }
    # 1st fetchone: no existing user by email -> None
    # 2nd fetchone: username availability check -> None (available)
    # 3rd fetchone: re-fetch newly inserted user -> new_user_row
    cursor.fetchone.side_effect = [None, None, new_user_row]
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"email": "newuser@example.com", "code": "123456"}):
        with _session({}) as sess:
            response, status = AuthController.google_verify_otp()

    assert status == 200
    assert sess["user"]["username"] == "newuser"


# ── dashboard ────────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_dashboard_redirects_when_not_logged_in(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context():
        with _session({}):
            controller = AuthController()
            result = controller.dashboard()

    assert result == "REDIRECT"


@patch("app.controlers.auth_control.render_template", return_value="DASHBOARD")
@patch("app.controlers.auth_control.get_db_connection")
def test_dashboard_renders_for_logged_in_user(mock_get_db, mock_render):
    conn, cursor = _mock_conn()
    db_user = {
        "id": 1, "username": "alice", "email": "alice@example.com", "status": "active",
        "first_name": None, "last_name": None, "phone": None, "city": None, "bio": None,
        "language": None, "role": None, "avatar": None, "cover": None, "theme_preference": None,
    }
    # fetchone calls: [0] users-by-id, [1] wishlist count
    cursor.fetchone.side_effect = [db_user, {"count": 1}]
    # fetchall calls: [0] bookings, [1] availability grouping, [2] notifications
    cursor.fetchall.side_effect = [[], [], []]
    mock_get_db.return_value = conn

    with _app.test_request_context():
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.dashboard()

    assert result == "DASHBOARD"
    kwargs = mock_render.call_args[1]
    assert kwargs["stats"]["total"] == 0


@patch("app.controlers.auth_control.flash")
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
@patch("app.controlers.auth_control.get_db_connection")
def test_dashboard_suspended_account_logs_out(mock_get_db, mock_url_for, mock_redirect, mock_flash):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"id": 1, "status": "suspended"}
    mock_get_db.return_value = conn
    mock_redirect.return_value = "REDIRECT"

    session_dict = {"user": {"id": 1}}
    with _app.test_request_context():
        with _session(session_dict):
            controller = AuthController()
            result = controller.dashboard()

    assert session_dict == {}
    mock_flash.assert_called_once()
    assert result == "REDIRECT"


# ── cancel_booking ───────────────────────────────────────────────────────
def test_cancel_booking_unauthenticated_returns_401():
    with _app.test_request_context(method="POST", data={}):
        with _session({}):
            controller = AuthController()
            response, status = controller.cancel_booking()

    assert status == 401


def test_cancel_booking_missing_id_returns_400():
    with _app.test_request_context(method="POST", data={}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.cancel_booking()

    assert status == 400


@patch("app.controlers.auth_control.get_db_connection")
def test_cancel_booking_not_found_returns_404(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = None
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", data={"booking_id": "5"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.cancel_booking()

    assert status == 404


@patch("app.controlers.auth_control.get_db_connection")
def test_cancel_booking_not_confirmed_returns_400(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"id": 5, "status": "cancelled", "activity": "Paragliding", "date": "2026-07-01"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", data={"booking_id": "5"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.cancel_booking()

    assert status == 400


@patch("app.controlers.auth_control.get_db_connection")
def test_cancel_booking_success(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"id": 5, "status": "confirmed", "activity": "Paragliding", "date": "2026-07-01"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", data={"booking_id": "5"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.cancel_booking()

    assert status == 200
    assert response.json["success"] is True


@patch("app.controlers.auth_control.get_db_connection")
def test_cancel_booking_db_exception_returns_500(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.side_effect = Exception("db exploded")
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", data={"booking_id": "5"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.cancel_booking()

    assert status == 500


# ── book_activity ────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_book_activity_redirects_when_not_logged_in(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context(method="GET"):
        with _session({}):
            controller = AuthController()
            result = controller.book_activity()

    assert result == "REDIRECT"


@patch("app.controlers.auth_control.flash")
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
@patch("app.controlers.auth_control.get_db_connection")
def test_book_activity_post_creates_booking(mock_get_db, mock_url_for, mock_redirect, mock_flash):
    conn, cursor = _mock_conn()
    mock_get_db.return_value = conn
    mock_redirect.return_value = "REDIRECT"

    with _app.test_request_context(
        method="POST",
        data={"activity_id": "paragliding", "date": "2026-07-01", "people": "2"},
    ):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.book_activity()

    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()
    mock_flash.assert_called_once()
    assert result == "REDIRECT"


@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_book_activity_unknown_activity_defaults_to_paragliding_but_skips_db_without_date(
    mock_url_for, mock_redirect
):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context(method="POST", data={"activity_id": "unknown-thing"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.book_activity()

    # No `date` provided -> booking insert block is skipped entirely.
    assert result == "REDIRECT"


# ── manage ───────────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_manage_redirects_when_not_logged_in(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context():
        with _session({}):
            controller = AuthController()
            result = controller.manage()

    assert result == "REDIRECT"


@patch("app.controlers.auth_control.render_template", return_value="MANAGE_PAGE")
@patch("app.controlers.auth_control.get_db_connection")
def test_manage_get_renders_profile_page(mock_get_db, mock_render):
    conn, cursor = _mock_conn()
    cursor.fetchone.side_effect = [{"id": 1, "username": "alice"}, {"count": 0}]
    mock_get_db.return_value = conn

    with _app.test_request_context(method="GET"):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.manage()

    assert result == "MANAGE_PAGE"


@patch("app.controlers.auth_control.get_db_connection")
def test_manage_post_json_updates_profile(mock_get_db):
    conn, cursor = _mock_conn()
    updated_user = {
        "id": 1, "username": "alice", "email": "new@example.com", "first_name": "New",
        "last_name": None, "phone": None, "city": None, "bio": None, "language": None,
        "role": None, "avatar": None, "cover": None, "theme_preference": None,
    }
    cursor.fetchone.return_value = updated_user
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"email": "new@example.com", "firstName": "New"}):
        with _session({"user": {"id": 1}}) as sess:
            controller = AuthController()
            response, status = controller.manage()

    assert status == 200
    assert response.json["status"] == "success"
    assert sess["user"]["email"] == "new@example.com"


@patch("app.controlers.auth_control.get_db_connection")
def test_manage_post_json_db_error_returns_500(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.side_effect = Exception("db exploded")
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"email": "x@example.com"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.manage()

    assert status == 500
    assert response.json["status"] == "error"


# ── wishlist_page ────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_wishlist_page_redirects_when_not_logged_in(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context():
        with _session({}):
            controller = AuthController()
            result = controller.wishlist_page()

    assert result == "REDIRECT"


@patch("app.controlers.auth_control.render_template", return_value="WISHLIST")
@patch("app.controlers.auth_control.get_db_connection")
def test_wishlist_page_includes_static_activity_items(mock_get_db, mock_render):
    conn, cursor = _mock_conn()
    cursor.fetchall.return_value = [{"activity_id": "paragliding"}]
    mock_get_db.return_value = conn

    with _app.test_request_context():
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.wishlist_page()

    assert result == "WISHLIST"
    kwargs = mock_render.call_args[1]
    assert kwargs["wishlist"][0]["name"] == "Paragliding"


# ── toggle_wishlist ──────────────────────────────────────────────────────
def test_toggle_wishlist_unauthenticated_returns_401():
    with _app.test_request_context(method="POST", json={}):
        with _session({}):
            controller = AuthController()
            response, status = controller.toggle_wishlist()

    assert status == 401


def test_toggle_wishlist_invalid_activity_returns_400():
    with _app.test_request_context(method="POST", json={"activity_id": "not-a-real-activity"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.toggle_wishlist()

    assert status == 400


@patch("app.controlers.auth_control.get_db_connection")
def test_toggle_wishlist_adds_when_not_already_saved(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = None
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"activity_id": "paragliding"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.toggle_wishlist()

    assert status == 200
    assert response.json["saved"] is True


@patch("app.controlers.auth_control.get_db_connection")
def test_toggle_wishlist_removes_when_already_saved(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"user_id": 1, "activity_id": "paragliding"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"activity_id": "paragliding"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.toggle_wishlist()

    assert status == 200
    assert response.json["saved"] is False


# ── forgot_password ──────────────────────────────────────────────────────
def test_forgot_password_get_renders_reset_page():
    with _app.test_request_context(method="GET"):
        with patch("app.controlers.auth_control.render_template", return_value="RESET_PAGE") as mock_render:
            controller = AuthController()
            result = controller.forgot_password()

    assert result == "RESET_PAGE"
    mock_render.assert_called_once_with("reset.html")


def test_forgot_password_send_otp_missing_email_returns_400():
    with _app.test_request_context(method="POST", json={"action": "send_otp"}):
        controller = AuthController()
        response, status = controller.forgot_password()

    assert status == 400


@patch("app.controlers.auth_control.get_db_connection")
def test_forgot_password_send_otp_unregistered_email_returns_404(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = None
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"action": "send_otp", "email": "ghost@example.com"}):
        controller = AuthController()
        response, status = controller.forgot_password()

    assert status == 404


@patch("app.controlers.auth_control.send_email", return_value=True)
@patch("builtins.open", new_callable=MagicMock)
@patch("app.controlers.auth_control.get_db_connection")
def test_forgot_password_send_otp_success(mock_get_db, mock_open, mock_send_email):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"id": 1, "email": "alice@example.com"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"action": "send_otp", "email": "alice@example.com"}):
        controller = AuthController()
        response, status = controller.forgot_password()

    assert status == 200
    assert "alice@example.com" in otp_store


def test_forgot_password_reset_missing_fields_returns_400():
    with _app.test_request_context(method="POST", json={"action": "reset", "email": "a@example.com"}):
        controller = AuthController()
        response, status = controller.forgot_password()

    assert status == 400


def test_forgot_password_reset_no_otp_record_returns_400():
    with _app.test_request_context(
        method="POST",
        json={"action": "reset", "email": "a@example.com", "code": "123456", "password": "newpw"},
    ):
        controller = AuthController()
        response, status = controller.forgot_password()

    assert status == 400


def test_forgot_password_reset_wrong_code_returns_400():
    import time
    otp_store["a@example.com"] = {"code": "123456", "expires_at": time.time() + 100}

    with _app.test_request_context(
        method="POST",
        json={"action": "reset", "email": "a@example.com", "code": "000000", "password": "newpw"},
    ):
        controller = AuthController()
        response, status = controller.forgot_password()

    assert status == 400


@patch("app.controlers.auth_control.get_db_connection")
def test_forgot_password_reset_success(mock_get_db):
    import time
    otp_store["a@example.com"] = {"code": "123456", "expires_at": time.time() + 100}
    conn, cursor = _mock_conn()
    mock_get_db.return_value = conn

    with _app.test_request_context(
        method="POST",
        json={"action": "reset", "email": "a@example.com", "code": "123456", "password": "newpw"},
    ):
        controller = AuthController()
        response, status = controller.forgot_password()

    assert status == 200
    assert "a@example.com" not in otp_store


# ── gallery ──────────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.render_template", return_value="GALLERY")
@patch("app.controlers.auth_control.get_db_connection")
def test_gallery_renders_posts(mock_get_db, mock_render):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchall.return_value = [{"id": 1, "title": "Sunrise", "username": "alice"}]
    mock_get_db.return_value = conn

    with _app.test_request_context():
        with _session({}):
            controller = AuthController()
            result = controller.gallery()

    assert result == "GALLERY"
    kwargs = mock_render.call_args[1]
    assert kwargs["posts"][0]["title"] == "Sunrise"


# ── gallery_add ──────────────────────────────────────────────────────────
def test_gallery_add_unauthenticated_returns_401():
    with _app.test_request_context(method="POST"):
        with _session({}):
            controller = AuthController()
            response, status = controller.gallery_add()

    assert status == 401


@patch("app.controlers.auth_control.get_db_connection")
def test_gallery_add_non_admin_returns_403(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"status": "active"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST"):
        with _session({"user": {"id": 1, "role": "Adventure Seeker"}}):
            controller = AuthController()
            response, status = controller.gallery_add()

    assert status == 403


@patch("app.controlers.auth_control.get_db_connection")
def test_gallery_add_missing_image_returns_400(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"status": "active"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", data={"title": "Test"}):
        with _session({"user": {"id": 1, "role": "admin"}}):
            controller = AuthController()
            response, status = controller.gallery_add()

    assert status == 400


@patch("os.makedirs")
@patch("app.controlers.auth_control.get_db_connection")
def test_gallery_add_success(mock_get_db, mock_makedirs):
    import io
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"status": "active"}
    mock_get_db.return_value = conn

    data = {
        "title": "Test",
        "description": "desc",
        "image": (io.BytesIO(b"fake image bytes"), "photo.jpg"),
    }

    with _app.test_request_context(method="POST", data=data, content_type="multipart/form-data"):
        with _session({"user": {"id": 1, "role": "admin"}}):
            with patch("werkzeug.datastructures.FileStorage.save"):
                controller = AuthController()
                response = controller.gallery_add()

    assert response.json["success"] is True


# ── gallery_delete ───────────────────────────────────────────────────────
def test_gallery_delete_non_admin_returns_403():
    with _app.test_request_context(method="POST"):
        with _session({"user": {"id": 1, "role": "Adventure Seeker"}}):
            controller = AuthController()
            response, status = controller.gallery_delete(1)

    assert status == 403


@patch("app.controlers.auth_control.get_db_connection")
def test_gallery_delete_not_found_returns_404(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchone.return_value = None
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST"):
        with _session({"user": {"id": 1, "role": "admin"}}):
            controller = AuthController()
            response, status = controller.gallery_delete(99)

    assert status == 404


@patch("os.path.exists", return_value=False)
@patch("app.controlers.auth_control.get_db_connection")
def test_gallery_delete_success(mock_get_db, mock_exists):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchone.return_value = {"id": 1, "image_url": "gallery/x.jpg"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST"):
        with _session({"user": {"id": 1, "role": "admin"}}):
            controller = AuthController()
            response = controller.gallery_delete(1)

    assert response.json["success"] is True


# ── reviews ──────────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.render_template", return_value="REVIEWS")
@patch("app.controlers.auth_control.get_db_connection")
def test_reviews_renders_review_list(mock_get_db, mock_render):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchall.return_value = [{"id": 1, "review": "Great!", "username": "alice"}]
    mock_get_db.return_value = conn

    with _app.test_request_context():
        with _session({}):
            controller = AuthController()
            result = controller.reviews()

    assert result == "REVIEWS"
    kwargs = mock_render.call_args[1]
    assert kwargs["reviews"][0]["review"] == "Great!"


# ── add_review ───────────────────────────────────────────────────────────
@patch("app.controlers.auth_control.flash")
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_add_review_not_logged_in_redirects(mock_url_for, mock_redirect, mock_flash):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context(method="POST"):
        with _session({}):
            controller = AuthController()
            result = controller.add_review()

    assert result == "REDIRECT"


@patch("app.controlers.auth_control.flash")
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
def test_add_review_missing_fields_redirects(mock_url_for, mock_redirect, mock_flash):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context(method="POST", data={"activity": ""}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.add_review()

    assert result == "REDIRECT"


@patch("app.controlers.auth_control.flash")
@patch("app.controlers.auth_control.redirect")
@patch("app.controlers.auth_control.url_for")
@patch("app.controlers.auth_control.get_db_connection")
def test_add_review_success_clamps_rating(mock_get_db, mock_url_for, mock_redirect, mock_flash):
    conn, cursor = _mock_conn()
    mock_get_db.return_value = conn
    mock_redirect.return_value = "REDIRECT"

    with _app.test_request_context(
        method="POST", data={"activity": "Paragliding", "rating": "99", "review": "Amazing!"}
    ):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.add_review()

    insert_args = cursor.execute.call_args[0][1]
    assert insert_args[2] == 5  # clamped to max
    assert result == "REDIRECT"


# ── edit_review ──────────────────────────────────────────────────────────
def test_edit_review_unauthenticated_returns_401():
    with _app.test_request_context(method="POST", json={}):
        with _session({}):
            controller = AuthController()
            response, status = controller.edit_review(1)

    assert status == 401


@patch("app.controlers.auth_control.get_db_connection")
def test_edit_review_not_found_returns_404(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchone.return_value = None
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={}):
        with _session({"user": {"id": 1, "role": "Adventure Seeker"}}):
            controller = AuthController()
            response, status = controller.edit_review(99)

    assert status == 404


@patch("app.controlers.auth_control.get_db_connection")
def test_edit_review_permission_denied_returns_403(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchone.return_value = {"id": 1, "user_id": 2, "rating": 4, "review": "ok"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={}):
        with _session({"user": {"id": 1, "role": "Adventure Seeker"}}):
            controller = AuthController()
            response, status = controller.edit_review(1)

    assert status == 403


@patch("app.controlers.auth_control.get_db_connection")
def test_edit_review_owner_can_update(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchone.return_value = {"id": 1, "user_id": 1, "rating": 4, "review": "ok"}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", json={"review": "Updated!", "rating": 5}):
        with _session({"user": {"id": 1, "role": "Adventure Seeker"}}):
            controller = AuthController()
            response = controller.edit_review(1)

    assert response.json["success"] is True


# ── delete_review ────────────────────────────────────────────────────────
def test_delete_review_unauthenticated_returns_401():
    with _app.test_request_context(method="POST"):
        with _session({}):
            controller = AuthController()
            response, status = controller.delete_review(1)

    assert status == 401


@patch("app.controlers.auth_control.get_db_connection")
def test_delete_review_not_found_returns_404(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchone.return_value = None
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST"):
        with _session({"user": {"id": 1, "role": "Adventure Seeker"}}):
            controller = AuthController()
            response, status = controller.delete_review(99)

    assert status == 404


@patch("app.controlers.auth_control.get_db_connection")
def test_delete_review_owner_can_delete(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchone.return_value = {"id": 1, "user_id": 1}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST"):
        with _session({"user": {"id": 1, "role": "Adventure Seeker"}}):
            controller = AuthController()
            response = controller.delete_review(1)

    assert response.json["success"] is True


@patch("app.controlers.auth_control.get_db_connection")
def test_delete_review_non_owner_non_admin_returns_403(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.return_value.fetchone.return_value = {"id": 1, "user_id": 2}
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST"):
        with _session({"user": {"id": 1, "role": "Adventure Seeker"}}):
            controller = AuthController()
            response, status = controller.delete_review(1)

    assert status == 403


# ── mark_notification_read ───────────────────────────────────────────────
def test_mark_notification_read_unauthenticated_returns_401():
    with _app.test_request_context(method="POST", data={}):
        with _session({}):
            controller = AuthController()
            response, status = controller.mark_notification_read()

    assert status == 401


def test_mark_notification_read_missing_id_returns_400():
    with _app.test_request_context(method="POST", json={}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.mark_notification_read()

    assert status == 400


@patch("app.controlers.auth_control.get_db_connection")
def test_mark_notification_read_success(mock_get_db):
    conn, cursor = _mock_conn()
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", data={"id": "7"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response = controller.mark_notification_read()

    assert response.json["success"] is True


@patch("app.controlers.auth_control.get_db_connection")
def test_mark_notification_read_db_error_returns_500(mock_get_db):
    conn, cursor = _mock_conn()
    cursor.execute.side_effect = Exception("db exploded")
    mock_get_db.return_value = conn

    with _app.test_request_context(method="POST", data={"id": "7"}):
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            response, status = controller.mark_notification_read()

    assert status == 500
