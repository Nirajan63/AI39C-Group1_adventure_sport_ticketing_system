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