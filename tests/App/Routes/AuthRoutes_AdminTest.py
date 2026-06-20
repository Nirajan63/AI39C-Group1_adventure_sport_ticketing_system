"""
Test stub for App/Routes/AuthRoutes_Admin.py

Covers:
    - AuthRoutes_Admin.__init__()
    - AuthRoutes_Admin.register()
"""
import unittest


class AuthRoutesAdminTest(unittest.TestCase):
    """Tests for the admin-facing AuthRoutes_Admin registrar."""

    def setUp(self):
        # TODO: instantiate AuthRoutes_Admin() and a Flask app/blueprint to
        # register against
        pass

    def test_init_sets_up_expected_attributes(self):
        # TODO: assert __init__() initializes the admin controller/blueprint
        # references AuthRoutes_Admin depends on
        pass

    def test_register_adds_expected_url_rules(self):
        # TODO: assert register() adds all expected admin routes (login,
        # dashboard, api_* endpoints, etc.) to the Flask app
        pass

    def test_register_routes_map_to_correct_view_functions(self):
        # TODO: assert each registered route maps to the correct
        # AuthController_Admin method
        pass

    def test_register_protects_admin_routes(self):
        # TODO: assert admin-only routes are wrapped with admin_required
        # (or equivalent) protection
        pass


if __name__ == "__main__":
    unittest.main()
