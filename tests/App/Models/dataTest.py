"""
Test stub for App/Models/data.py

Covers:
    - Database.__init__()
    - Database._check_connection()
    - Database._prepare_query()
    - Database.fetch_one()
    - Database.fetch_all()
    - Database.execute()
    - Database.close()
    - Database.create_tables() (static)
"""
import unittest


class DatabaseTest(unittest.TestCase):
    """Tests for the Database wrapper class."""

    def setUp(self):
        # TODO: instantiate Database() against a temporary/test database
        pass

    def tearDown(self):
        # TODO: close connections / clean up test database artifacts
        pass

    def test_init_establishes_connection(self):
        # TODO: assert __init__() successfully opens a database connection
        pass

    def test_check_connection_detects_open_connection(self):
        # TODO: assert _check_connection() returns/affirms an active connection
        pass

    def test_check_connection_handles_closed_connection(self):
        # TODO: assert _check_connection() reconnects or raises appropriately
        # when the connection is closed
        pass

    def test_prepare_query_formats_query_correctly(self):
        # TODO: assert _prepare_query(query) returns the expected prepared
        # statement/string
        pass

    def test_fetch_one_returns_single_row(self):
        # TODO: assert fetch_one(query, params) returns a single matching row
        pass

    def test_fetch_one_returns_none_when_no_match(self):
        # TODO: assert fetch_one() returns None when no rows match
        pass

    def test_fetch_all_returns_all_rows(self):
        # TODO: assert fetch_all(query, params) returns all matching rows
        pass

    def test_fetch_all_returns_empty_list_when_no_match(self):
        # TODO: assert fetch_all() returns an empty list when nothing matches
        pass

    def test_execute_runs_statement_and_commits(self):
        # TODO: assert execute(query, params) runs and commits the statement
        pass

    def test_execute_handles_invalid_query(self):
        # TODO: assert execute() raises/handles errors for invalid SQL
        pass

    def test_close_closes_connection(self):
        # TODO: assert close() properly closes the underlying connection
        pass

    def test_create_tables_creates_expected_schema(self):
        # TODO: assert create_tables() (static method) creates all expected
        # tables in a fresh database
        pass


if __name__ == "__main__":
    unittest.main()
