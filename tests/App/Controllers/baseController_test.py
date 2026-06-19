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
    