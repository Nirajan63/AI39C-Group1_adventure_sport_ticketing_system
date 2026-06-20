"""
Test stub for run.py

Covers:
    - app creation via create_app()
    - debug_mode / port resolution from environment variables
"""
import unittest


class RunTest(unittest.TestCase):
    """Tests for the application entry point."""

    def setUp(self):
        # TODO: set up any environment variables / mocks needed before
        # importing run.py (e.g. FLASK_DEBUG, PORT)
        pass

    def test_app_is_created(self):
        # TODO: assert `app` is a valid Flask application instance
        pass

    def test_debug_mode_defaults_to_false(self):
        # TODO: assert debug_mode resolves to False when FLASK_DEBUG is unset
        pass

    def test_debug_mode_true_when_env_set(self):
        # TODO: assert debug_mode resolves to True when FLASK_DEBUG="true"
        pass

    def test_port_defaults_to_5000(self):
        # TODO: assert port resolves to 5000 when PORT env var is unset
        pass

    def test_port_reads_from_env(self):
        # TODO: assert port resolves correctly when PORT env var is set
        pass


if __name__ == "__main__":
    unittest.main()
