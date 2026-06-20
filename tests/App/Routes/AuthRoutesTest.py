"""
Test stub for App/Routes/AuthRoutes.py

Covers:
    - AuthRoutes.__init__()
    - AuthRoutes.register()
"""
import unittest


class AuthRoutesTest(unittest.TestCase):
    """Tests for the user-facing AuthRoutes registrar."""

    def setUp(self):
        # TODO: instantiate AuthRoutes() and a Flask app/blueprint to register against
        pass

    def test_init_sets_up_expected_attributes(self):
        # TODO: assert __init__() initializes the controller/blueprint
        # references AuthRoutes depends on
        pass

    def test_register_adds_expected_url_rules(self):
        # TODO: assert register() adds all expected routes (login, register,
        # logout, dashboard, booking, etc.) to the Flask app
        pass

    def test_register_routes_map_to_correct_view_functions(self):
        # TODO: assert each registered route maps to the correct
        # AuthController method
        pass


if __name__ == "__main__":
    unittest.main()
