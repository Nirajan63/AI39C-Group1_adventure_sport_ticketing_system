"""
Test stub for config.py

Covers:
    - SQLALCHEMY_DATABASE_URI
    - SECRET_KEY
"""
import unittest


class ConfigTest(unittest.TestCase):
    """Tests for application configuration values."""

    def setUp(self):
        # TODO: import config module fresh / reset relevant env vars here
        pass

    def test_sqlalchemy_database_uri_defaults_to_sqlite(self):
        # TODO: assert SQLALCHEMY_DATABASE_URI falls back to 'sqlite:///dev.db'
        # when the DATABASE_URI environment variable is not set
        pass

    def test_sqlalchemy_database_uri_reads_from_env(self):
        # TODO: assert SQLALCHEMY_DATABASE_URI uses DATABASE_URI env var when set
        pass

    def test_secret_key_defaults_to_fallback(self):
        # TODO: assert SECRET_KEY falls back to the insecure default when
        # SECRET_KEY environment variable is not set
        pass

    def test_secret_key_reads_from_env(self):
        # TODO: assert SECRET_KEY uses SECRET_KEY env var when set
        pass


if __name__ == "__main__":
    unittest.main()
