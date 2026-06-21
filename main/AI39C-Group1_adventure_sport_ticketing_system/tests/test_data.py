"""
Tests for app/models/data.py (Database).

Covers every method:
  - __init__
  - fetch_one
  - fetch_all
  - execute
  - close
  - create_tables (static)
"""
import pytest
from unittest.mock import patch, MagicMock

from app.models.data import Database


@patch("app.models.data.get_db_connection")
def test_init_opens_connection(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn

    db = Database()

    mock_get_db_connection.assert_called_once()
    assert db._connection is mock_conn


@patch("app.models.data.get_db_connection")
def test_fetch_one_with_params(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"id": 1}
    mock_get_db_connection.return_value = mock_conn

    db = Database()
    result = db.fetch_one("SELECT * FROM users WHERE id = %s", (1,))

    mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE id = %s", (1,))
    mock_cursor.close.assert_called_once()
    assert result == {"id": 1}


@patch("app.models.data.get_db_connection")
def test_fetch_one_without_params(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"total": 3}
    mock_get_db_connection.return_value = mock_conn

    db = Database()
    result = db.fetch_one("SELECT COUNT(*) AS total FROM users")

    mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) AS total FROM users")
    assert result == {"total": 3}


@patch("app.models.data.get_db_connection")
def test_fetch_all_with_params(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1}, {"id": 2}]
    mock_get_db_connection.return_value = mock_conn

    db = Database()
    result = db.fetch_all("SELECT * FROM users WHERE role = %s", ("admin",))

    mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE role = %s", ("admin",))
    mock_cursor.close.assert_called_once()
    assert result == [{"id": 1}, {"id": 2}]


@patch("app.models.data.get_db_connection")
def test_fetch_all_without_params(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_get_db_connection.return_value = mock_conn

    db = Database()
    result = db.fetch_all("SELECT * FROM users")

    mock_cursor.execute.assert_called_once_with("SELECT * FROM users")
    assert result == []


@patch("app.models.data.get_db_connection")
def test_execute_with_params_commits(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    db = Database()
    db.execute("UPDATE users SET role = %s WHERE id = %s", ("admin", 1))

    mock_cursor.execute.assert_called_once_with("UPDATE users SET role = %s WHERE id = %s", ("admin", 1))
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


@patch("app.models.data.get_db_connection")
def test_execute_without_params_commits(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    db = Database()
    db.execute("DELETE FROM sessions")

    mock_cursor.execute.assert_called_once_with("DELETE FROM sessions")
    mock_conn.commit.assert_called_once()


@patch("app.models.data.get_db_connection")
def test_close_closes_connection_when_present(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn

    db = Database()
    db.close()

    mock_conn.close.assert_called_once()


@patch("app.models.data.get_db_connection")
def test_close_does_nothing_when_connection_is_none(mock_get_db_connection):
    mock_get_db_connection.return_value = MagicMock()
    db = Database()
    db._connection = None

    # Should not raise even though there's no connection to close.
    db.close()


@patch("app.models.data.init_db")
def test_create_tables_calls_init_db(mock_init_db):
    Database.create_tables()

    mock_init_db.assert_called_once()
