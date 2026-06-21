"""
Tests for app/controlers/baseController.py (BaseController).

Covers every method:
  - get_form_data
  - is_logged_in
  - get_current_user_id
  - get_current_role
  - flash_and_redirect
"""
import pytest
from flask import Flask
from unittest.mock import patch

from app.controlers.baseController import BaseController

_app = Flask(__name__)


def test_get_form_data_returns_stripped_values():
    controller = BaseController()
    with _app.test_request_context(
        method="POST", data={"name": "  Alice  ", "email": "alice@example.com "}
    ):
        name, email = controller.get_form_data("name", "email")

        assert name == "Alice"
        assert email == "alice@example.com"


def test_get_form_data_defaults_missing_fields_to_empty_string():
    controller = BaseController()
    with _app.test_request_context(method="POST", data={}):
        result = controller.get_form_data("missing_field")

        assert result == ("",)


def test_is_logged_in_true_when_user_in_session():
    controller = BaseController()
    with patch("app.controlers.baseController.session", {"user": {"id": 1}}):
        assert controller.is_logged_in() is True


def test_is_logged_in_false_when_no_user_in_session():
    controller = BaseController()
    with patch("app.controlers.baseController.session", {}):
        assert controller.is_logged_in() is False


def test_get_current_user_id_returns_id_when_logged_in():
    controller = BaseController()
    with patch("app.controlers.baseController.session", {"user": {"id": 42}}):
        assert controller.get_current_user_id() == 42


def test_get_current_user_id_returns_none_when_not_logged_in():
    controller = BaseController()
    with patch("app.controlers.baseController.session", {}):
        assert controller.get_current_user_id() is None


def test_get_current_role_returns_role_when_logged_in():
    controller = BaseController()
    with patch("app.controlers.baseController.session", {"user": {"role": "admin"}}):
        assert controller.get_current_role() == "admin"


def test_get_current_role_returns_none_when_not_logged_in():
    controller = BaseController()
    with patch("app.controlers.baseController.session", {}):
        assert controller.get_current_role() is None


@patch("app.controlers.baseController.url_for")
@patch("app.controlers.baseController.redirect")
@patch("app.controlers.baseController.flash")
def test_flash_and_redirect_calls_flash_and_redirect(mock_flash, mock_redirect, mock_url_for):
    controller = BaseController()
    mock_url_for.return_value = "/somewhere"
    mock_redirect.return_value = "REDIRECT_RESPONSE"

    result = controller.flash_and_redirect("Done!", "success", "auth.dashboard")

    mock_flash.assert_called_once_with("Done!", "success")
    mock_url_for.assert_called_once_with("auth.dashboard")
    mock_redirect.assert_called_once_with("/somewhere")
    assert result == "REDIRECT_RESPONSE"
