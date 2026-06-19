"""
Test stub for App/Controllers/baseController.py

Covers:
    - BaseController.get_form_data()
    - BaseController.is_logged_in()
    - BaseController.get_current_user_id()
    - BaseController.get_current_role()
    - BaseController.flash_and_redirect()
"""
import unittest

class BaseControllerTest(unittest.TestCase):
    """Tests for the shared BaseController helper methods."""

    def setUp(self):
        # TODO: instantiate BaseController() within an app/request context
        pass

    def test_get_form_data_returns_requested_fields(self):
        # TODO: assert get_form_data(*fields) extracts only requested fields
        # from request.form
        pass
    
    def test_get_form_data_handles_missing_fields(self):
        # TODO: assert behavior when a requested field is absent from the form
        pass

    def test_is_logged_in_true_when_session_has_user(self):
        # TODO: assert is_logged_in() returns True when session contains user info
        pass

    def test_is_logged_in_false_when_session_empty(self):
        # TODO: assert is_logged_in() returns False when session is empty
        pass