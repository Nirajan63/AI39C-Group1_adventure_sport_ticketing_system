"""
Tests for app/Controllers/Auth.py (the legacy AuthController, imported via
the capitalized App.Controllers / App.Models package path).

Covers every method:
  login, register, logout, dashboard, book_activity.
"""
import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from contextlib import ExitStack

from app.controlers.Auth import AuthController, ACTIVITIES

_app = Flask(__name__)
_app.secret_key = "test-secret"


class _session:
    """is_logged_in() lives on BaseController and reads
    app.controlers.baseController.session, while AuthController's own
    methods read app.controlers.Auth.session directly -- patch both."""
    def __init__(self, value):
        self.value = value
        self._stack = ExitStack()

    def __enter__(self):
        self._stack.enter_context(patch("app.controlers.Auth.session", self.value))
        self._stack.enter_context(patch("app.controlers.baseController.session", self.value))
        return self.value

    def __exit__(self, *exc_info):
        return self._stack.__exit__(*exc_info)


# ── login ────────────────────────────────────────────────────────────────
@patch("app.controlers.Auth.redirect")
@patch("app.controlers.Auth.url_for")
def test_login_already_logged_in_redirects(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context():
        with _session({"user": {"id": 1}}):
            controller = AuthController()
            result = controller.login()

    assert result == "REDIRECT"


@patch("app.controlers.Auth.render_template", return_value="LOGIN_PAGE")
@patch("app.controlers.Auth.flash")
def test_login_post_missing_fields(mock_flash, mock_render):
    with _app.test_request_context(method="POST", data={}):
        with _session({}):
            controller = AuthController()
            result = controller.login()

    mock_flash.assert_called_once()
    assert result == "LOGIN_PAGE"


@patch("app.controlers.Auth.flash")
@patch("app.controlers.Auth.render_template", return_value="LOGIN_PAGE")
def test_login_post_invalid_credentials(mock_render, mock_flash):
    with _app.test_request_context(method="POST", data={"username": "ghost", "password": "x"}):
        with _session({}):
            controller = AuthController()
            with patch.object(controller.user_model, "find_by", return_value=None):
                result = controller.login()

    assert result == "LOGIN_PAGE"
    mock_flash.assert_called_once()


@patch("app.controlers.baseController.redirect")
@patch("app.controlers.baseController.url_for")
@patch("app.controlers.Auth.flash")
def test_login_post_success(mock_flash, mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    user_data = {"id": 1, "name": "alice", "email": "alice@example.com", "role": "Adventure Seeker", "password": "hashed"}

    with _app.test_request_context(method="POST", data={"username": "alice", "password": "correct"}):
        with _session({}) as sess:
            controller = AuthController()
            with patch.object(controller.user_model, "find_by", return_value=user_data):
                with patch("app.models.user.User.from_db") as mock_from_db:
                    fake_user = MagicMock()
                    fake_user.check_password.return_value = True
                    mock_from_db.return_value = fake_user
                    result = controller.login()

    assert sess["user"]["name"] == "alice"
    assert sess["user"]["username"] == "alice"
    assert result == "REDIRECT"


@patch("app.controlers.Auth.render_template", return_value="LOGIN_PAGE")
def test_login_get_renders_login_page(mock_render):
    with _app.test_request_context(method="GET"):
        with _session({}):
            controller = AuthController()
            result = controller.login()

    assert result == "LOGIN_PAGE"
    mock_render.assert_called_once_with("Login.html")


# ── register ─────────────────────────────────────────────────────────────
@patch("app.controlers.Auth.render_template", return_value="REGISTER_PAGE")
def test_register_get_renders_page(mock_render):
    with _app.test_request_context(method="GET"):
        controller = AuthController()
        result = controller.register()

    assert result == "REGISTER_PAGE"


@patch("app.controlers.Auth.flash")
@patch("app.controlers.Auth.render_template", return_value="REGISTER_PAGE")
def test_register_post_missing_fields(mock_render, mock_flash):
    with _app.test_request_context(method="POST", data={"username": "bob"}):
        controller = AuthController()
        result = controller.register()

    assert result == "REGISTER_PAGE"
    mock_flash.assert_called_once()


@patch("app.controlers.Auth.flash")
@patch("app.controlers.Auth.render_template", return_value="REGISTER_PAGE")
def test_register_post_email_already_exists(mock_render, mock_flash):
    with _app.test_request_context(
        method="POST", data={"username": "bob", "email": "bob@example.com", "password": "pw"}
    ):
        controller = AuthController()
        with patch("app.models.user.User.email_exists", return_value=True):
            result = controller.register()

    assert result == "REGISTER_PAGE"


@patch("app.controlers.Auth.redirect")
@patch("app.controlers.Auth.url_for")
@patch("app.controlers.Auth.flash")
def test_register_post_success(mock_flash, mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context(
        method="POST", data={"username": "newbob", "email": "newbob@example.com", "password": "pw"}
    ):
        controller = AuthController()
        with patch("app.models.user.User.email_exists", return_value=False):
            with patch("app.models.user.User.save") as mock_save:
                result = controller.register()

    mock_save.assert_called_once()
    assert result == "REDIRECT"


@patch("app.controlers.Auth.flash")
@patch("app.controlers.Auth.render_template", return_value="REGISTER_PAGE")
def test_register_post_save_failure_renders_error(mock_render, mock_flash):
    with _app.test_request_context(
        method="POST", data={"username": "newbob", "email": "newbob@example.com", "password": "pw"}
    ):
        controller = AuthController()
        with patch("app.models.user.User.email_exists", return_value=False):
            with patch("app.models.user.User.save", side_effect=Exception("db down")):
                result = controller.register()

    assert result == "REGISTER_PAGE"


# ── logout ───────────────────────────────────────────────────────────────
@patch("app.controlers.Auth.redirect")
@patch("app.controlers.Auth.url_for")
def test_logout_clears_session_and_redirects(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    session_dict = {"user": {"id": 1}}

    with _app.test_request_context():
        with patch("app.controlers.Auth.session", session_dict):
            controller = AuthController()
            result = controller.logout()

    assert session_dict == {}
    assert result == "REDIRECT"


# ── dashboard ────────────────────────────────────────────────────────────
@patch("app.controlers.Auth.redirect")
@patch("app.controlers.Auth.url_for")
def test_dashboard_redirects_when_not_logged_in(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context():
        with patch("app.controlers.Auth.session", {}):
            controller = AuthController()
            result = controller.dashboard()

    assert result == "REDIRECT"


@patch("app.controlers.Auth.render_template", return_value="DASHBOARD")
@patch("app.controlers.Auth.Database")
def test_dashboard_renders_with_enriched_bookings(mock_database_cls, mock_render):
    mock_db = MagicMock()
    mock_db.fetch_all.return_value = [
        {"id": 1, "activity": "Paragliding", "status": "confirmed", "total": 4500}
    ]
    mock_database_cls.return_value = mock_db

    with _app.test_request_context():
        with patch("app.controlers.Auth.session", {"user": {"id": 1, "name": "alice"}}):
            controller = AuthController()
            result = controller.dashboard()

    assert result == "DASHBOARD"
    kwargs = mock_render.call_args[1]
    assert kwargs["stats"]["total"] == 1
    assert kwargs["bookings"][0]["img"] == "Paragliding.png"


@patch("app.controlers.Auth.render_template", return_value="DASHBOARD")
@patch("app.controlers.Auth.Database")
def test_dashboard_backfills_username_and_joined(mock_database_cls, mock_render):
    mock_db = MagicMock()
    mock_db.fetch_all.return_value = []
    mock_database_cls.return_value = mock_db

    session_dict = {"user": {"id": 1, "name": "alice"}}
    with _app.test_request_context():
        with patch("app.controlers.Auth.session", session_dict):
            controller = AuthController()
            controller.dashboard()

    assert session_dict["user"]["username"] == "alice"
    assert session_dict["user"]["joined"] == "May 2026"


@patch("app.controlers.Auth.render_template", return_value="DASHBOARD")
@patch("app.controlers.Auth.Database")
def test_dashboard_unknown_activity_gets_default_metadata(mock_database_cls, mock_render):
    mock_db = MagicMock()
    mock_db.fetch_all.return_value = [
        {"id": 1, "activity": "Some Unknown Thing", "status": "completed", "total": 100}
    ]
    mock_database_cls.return_value = mock_db

    with _app.test_request_context():
        with patch("app.controlers.Auth.session", {"user": {"id": 1, "name": "alice"}}):
            controller = AuthController()
            controller.dashboard()

    kwargs = mock_render.call_args[1]
    assert kwargs["bookings"][0]["img"] == "Mountain-Main.png"
    assert kwargs["bookings"][0]["location"] == "Nepal"


# ── book_activity ────────────────────────────────────────────────────────
@patch("app.controlers.Auth.redirect")
@patch("app.controlers.Auth.url_for")
def test_book_activity_redirects_when_not_logged_in(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context(method="GET"):
        with patch("app.controlers.Auth.session", {}):
            controller = AuthController()
            result = controller.book_activity()

    assert result == "REDIRECT"


@patch("app.controlers.Auth.flash")
@patch("app.controlers.Auth.redirect")
@patch("app.controlers.Auth.url_for")
@patch("app.controlers.Auth.Database")
def test_book_activity_post_creates_booking(mock_database_cls, mock_url_for, mock_redirect, mock_flash):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db
    mock_redirect.return_value = "REDIRECT"

    with _app.test_request_context(
        method="POST", data={"activity_id": "paragliding", "date": "2026-07-01", "people": "2"}
    ):
        with patch("app.controlers.Auth.session", {"user": {"id": 1}}):
            controller = AuthController()
            result = controller.book_activity()

    mock_db.execute.assert_called_once()
    mock_flash.assert_called_once()
    assert result == "REDIRECT"


@patch("app.controlers.Auth.redirect")
@patch("app.controlers.Auth.url_for")
def test_book_activity_without_date_skips_db_insert(mock_url_for, mock_redirect):
    mock_redirect.return_value = "REDIRECT"
    with _app.test_request_context(method="POST", data={"activity_id": "paragliding"}):
        with patch("app.controlers.Auth.session", {"user": {"id": 1}}):
            controller = AuthController()
            result = controller.book_activity()

    assert result == "REDIRECT"


@patch("app.controlers.Auth.flash")
@patch("app.controlers.Auth.redirect")
@patch("app.controlers.Auth.url_for")
@patch("app.controlers.Auth.Database")
def test_book_activity_db_error_flashes_generic_message(mock_database_cls, mock_url_for, mock_redirect, mock_flash):
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("db exploded")
    mock_database_cls.return_value = mock_db
    mock_redirect.return_value = "REDIRECT"

    with _app.test_request_context(
        method="POST", data={"activity_id": "paragliding", "date": "2026-07-01"}
    ):
        with patch("app.controlers.Auth.session", {"user": {"id": 1}}):
            controller = AuthController()
            result = controller.book_activity()

    mock_flash.assert_called_once_with("An error occurred. Please try again.")
    assert result == "REDIRECT"


@patch("app.controlers.Auth.flash")
@patch("app.controlers.Auth.redirect")
@patch("app.controlers.Auth.url_for")
@patch("app.controlers.Auth.Database")
def test_book_activity_unknown_id_defaults_to_paragliding(mock_database_cls, mock_url_for, mock_redirect, mock_flash):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db
    mock_redirect.return_value = "REDIRECT"

    with _app.test_request_context(
        method="POST", data={"activity_id": "totally-unknown", "date": "2026-07-01"}
    ):
        with patch("app.controlers.Auth.session", {"user": {"id": 1}}):
            controller = AuthController()
            controller.book_activity()

    insert_args = mock_db.execute.call_args[0][1]
    assert insert_args[1] == "Paragliding"
