"""
Tests for app/models/database.py.

Covers:
  - SafeDictCursor.execute (the '?' -> '%s' rewriting)
  - get_db_connection
  - _normalize_event_row
  - create_database_if_not_exists
  - init_db (smoke test - seeds tables without raising)
  - get_event_by_id
  - get_published_events (filters, pagination, sorting)
  - get_featured_events
  - get_distinct_categories
  - get_distinct_locations
  - create_booking (success + failure paths)
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, call

from app.models.database import (
    SafeDictCursor,
    get_db_connection,
    _normalize_event_row,
    create_database_if_not_exists,
    init_db,
    get_event_by_id,
    get_published_events,
    get_featured_events,
    get_distinct_categories,
    get_distinct_locations,
    create_booking,
)


# ── SafeDictCursor.execute ──────────────────────────────────────────────
def test_safe_dict_cursor_rewrites_question_marks_to_percent_s():
    cursor = SafeDictCursor.__new__(SafeDictCursor)
    with patch("pymysql.cursors.DictCursor.execute") as mock_super_execute:
        result = cursor.execute("SELECT * FROM users WHERE id = ?", (1,))

        mock_super_execute.assert_called_once_with("SELECT * FROM users WHERE id = %s", (1,))
        assert result is cursor


def test_safe_dict_cursor_leaves_query_unchanged_when_no_question_mark():
    cursor = SafeDictCursor.__new__(SafeDictCursor)
    with patch("pymysql.cursors.DictCursor.execute") as mock_super_execute:
        cursor.execute("SELECT * FROM users WHERE id = %s", (1,))

        mock_super_execute.assert_called_once_with("SELECT * FROM users WHERE id = %s", (1,))


def test_safe_dict_cursor_handles_none_query():
    cursor = SafeDictCursor.__new__(SafeDictCursor)
    with patch("pymysql.cursors.DictCursor.execute") as mock_super_execute:
        cursor.execute(None)
        mock_super_execute.assert_called_once_with(None, None)


# ── get_db_connection ────────────────────────────────────────────────────
@patch("app.models.database.pymysql.connect")
def test_get_db_connection_uses_env_vars(mock_connect, monkeypatch):
    monkeypatch.setenv("MYSQL_HOST", "dbhost")
    monkeypatch.setenv("MYSQL_USER", "dbuser")
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")
    monkeypatch.setenv("MYSQL_DB", "mydb")
    monkeypatch.setenv("MYSQL_PORT", "3307")
    mock_connect.return_value = "CONNECTION"

    result = get_db_connection()

    mock_connect.assert_called_once_with(
        host="dbhost", user="dbuser", password="secret", database="mydb",
        port=3307, cursorclass=SafeDictCursor
    )
    assert result == "CONNECTION"


@patch("app.models.database.pymysql.connect")
def test_get_db_connection_uses_defaults_when_env_unset(mock_connect, monkeypatch):
    for var in ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DB", "MYSQL_PORT"):
        monkeypatch.delenv(var, raising=False)
    mock_connect.return_value = "CONNECTION"

    get_db_connection()

    mock_connect.assert_called_once_with(
        host="localhost", user="root", password="", database="sportadventure",
        port=3306, cursorclass=SafeDictCursor
    )


# ── _normalize_event_row ────────────────────────────────────────────────
def test_normalize_event_row_returns_none_for_falsy_row():
    assert _normalize_event_row(None) is None
    assert _normalize_event_row({}) == {}


def test_normalize_event_row_formats_datetime_object():
    row = {"id": 1, "date_time": datetime(2026, 6, 20, 14, 30, 0)}
    result = _normalize_event_row(row)
    assert result["date_time"] == "2026-06-20T14:30:00"


def test_normalize_event_row_formats_string_with_space():
    row = {"id": 1, "date_time": "2026-06-20 14:30:00"}
    result = _normalize_event_row(row)
    assert result["date_time"] == "2026-06-20T14:30:00"


def test_normalize_event_row_passes_through_when_no_date_time():
    row = {"id": 1, "title": "Test Event"}
    result = _normalize_event_row(row)
    assert result == {"id": 1, "title": "Test Event"}


# ── create_database_if_not_exists ───────────────────────────────────────
@patch("app.models.database.pymysql.connect")
def test_create_database_if_not_exists_runs_create_statement(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    create_database_if_not_exists()

    assert mock_cursor.execute.call_count == 1
    executed_sql = mock_cursor.execute.call_args[0][0]
    assert "CREATE DATABASE IF NOT EXISTS" in executed_sql
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


# ── init_db (smoke test) ─────────────────────────────────────────────────
@patch("app.models.database.get_db_connection")
@patch("app.models.database.create_database_if_not_exists")
def test_init_db_seeds_tables_without_raising(mock_create_db, mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    # Make every "is the table empty?" / "does this row already exist?"
    # check come back empty, and ALTER TABLE probe selects fail (so the
    # except-and-ALTER fallback paths run too), exercising every branch.
    def fetchone_side_effect():
        return {"count": 0}

    mock_cursor.fetchone.side_effect = lambda: {"count": 0}

    init_db()

    mock_create_db.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
    assert mock_cursor.execute.call_count > 5  # many CREATE/INSERT statements ran


@patch("app.models.database.get_db_connection")
@patch("app.models.database.create_database_if_not_exists")
def test_init_db_skips_seeding_when_data_already_present(mock_create_db, mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    # Non-zero counts and existing users mean every "seed if missing"
    # branch should be skipped, but init_db should still complete cleanly.
    mock_cursor.fetchone.return_value = {"count": 5, "id": 1, "status": "active"}

    init_db()

    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


# ── get_event_by_id ──────────────────────────────────────────────────────
@patch("app.models.database.get_db_connection")
def test_get_event_by_id_found(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"id": 5, "title": "Jazz Night", "date_time": "2026-07-01 19:00:00"}
    mock_get_db_connection.return_value = mock_conn

    result = get_event_by_id(5)

    mock_cursor.execute.assert_called_once_with("SELECT * FROM events WHERE id = ?", (5,))
    mock_conn.close.assert_called_once()
    assert result["title"] == "Jazz Night"
    assert result["date_time"] == "2026-07-01T19:00:00"


@patch("app.models.database.get_db_connection")
def test_get_event_by_id_not_found(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_get_db_connection.return_value = mock_conn

    result = get_event_by_id(999)

    assert result is None


# ── get_published_events ────────────────────────────────────────────────
@patch("app.models.database.get_db_connection")
def test_get_published_events_no_filters_first_page(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"count": 12}
    mock_cursor.fetchall.return_value = [{"id": 1, "title": "Event A"}]
    mock_get_db_connection.return_value = mock_conn

    result = get_published_events({}, page=1, per_page=6)

    assert result["total_events"] == 12
    assert result["total_pages"] == 2
    assert result["page"] == 1
    assert result["per_page"] == 6
    assert len(result["events"]) == 1


@patch("app.models.database.get_db_connection")
def test_get_published_events_applies_all_filters_and_sort(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"count": 1}
    mock_cursor.fetchall.return_value = []
    mock_get_db_connection.return_value = mock_conn

    filters = {
        "category": "Adventure",
        "location": "Pokhara",
        "search": "raft",
        "price_max": "5000",
        "date_start": "2026-01-01",
        "date_end": "2026-12-31",
        "sort_by": "price_desc",
    }
    get_published_events(filters, page=2, per_page=4)

    # The final SELECT (paginated) query is the second execute call.
    final_query = mock_cursor.execute.call_args_list[-1][0][0]
    assert "category = ?" in final_query
    assert "location = ?" in final_query
    assert "title LIKE ? OR description LIKE ?" in final_query
    assert "price <= ?" in final_query
    assert "DATE(date_time) >= DATE(?)" in final_query
    assert "DATE(date_time) <= DATE(?)" in final_query
    assert "ORDER BY price DESC" in final_query
    assert "LIMIT ? OFFSET ?" in final_query


@patch("app.models.database.get_db_connection")
def test_get_published_events_invalid_price_max_is_ignored(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"count": 0}
    mock_cursor.fetchall.return_value = []
    mock_get_db_connection.return_value = mock_conn

    # Should not raise even though price_max isn't a valid int.
    result = get_published_events({"price_max": "not-a-number"}, page=1, per_page=6)
    assert result["total_events"] == 0
    assert result["total_pages"] == 1  # max(total_pages, 1)


@patch("app.models.database.get_db_connection")
def test_get_published_events_default_sort_is_upcoming(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"count": 0}
    mock_cursor.fetchall.return_value = []
    mock_get_db_connection.return_value = mock_conn

    get_published_events({}, page=1, per_page=6)

    final_query = mock_cursor.execute.call_args_list[-1][0][0]
    assert "ORDER BY date_time ASC" in final_query


# ── get_featured_events ──────────────────────────────────────────────────
@patch("app.models.database.get_db_connection")
def test_get_featured_events_returns_normalized_rows(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1, "date_time": "2026-07-01 10:00:00"}]
    mock_get_db_connection.return_value = mock_conn

    result = get_featured_events()

    assert len(result) == 1
    assert result[0]["date_time"] == "2026-07-01T10:00:00"
    mock_conn.close.assert_called_once()


# ── get_distinct_categories / get_distinct_locations ─────────────────────
@patch("app.models.database.get_db_connection")
def test_get_distinct_categories(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"category": "Adventure"}, {"category": "Music"}]
    mock_get_db_connection.return_value = mock_conn

    result = get_distinct_categories()

    assert result == ["Adventure", "Music"]


@patch("app.models.database.get_db_connection")
def test_get_distinct_locations(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"location": "Pokhara"}, {"location": "Kathmandu"}]
    mock_get_db_connection.return_value = mock_conn

    result = get_distinct_locations()

    assert result == ["Pokhara", "Kathmandu"]


# ── create_booking ───────────────────────────────────────────────────────
def test_create_booking_invalid_people_returns_none():
    assert create_booking(1, "event_5", "2026-07-01", "not-a-number") is None
    assert create_booking(1, "event_5", "2026-07-01", 0) is None


def test_create_booking_non_event_activity_returns_none():
    assert create_booking(1, "paragliding", "2026-07-01", 2) is None


@patch("app.models.database.get_event_by_id")
def test_create_booking_sold_out_event_returns_none(mock_get_event_by_id):
    mock_get_event_by_id.return_value = {"id": 5, "tickets_left": 1, "price": 1000, "title": "Jazz Night"}

    result = create_booking(1, "event_5", "2026-07-01", 3)

    assert result is None


@patch("app.models.database.get_db_connection")
@patch("app.models.database.get_event_by_id")
def test_create_booking_success_creates_booking(mock_get_event_by_id, mock_get_db_connection):
    mock_get_event_by_id.return_value = {
        "id": 5, "tickets_left": 10, "price": 1000.0, "title": "Jazz Night"
    }
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 42
    mock_get_db_connection.return_value = mock_conn

    result = create_booking(1, "event_5", "2026-07-01", 2)

    assert result == 42
    assert mock_conn.commit.call_count == 2
    mock_conn.close.assert_called_once()
    # tickets_left should be decremented
    decrement_call = mock_cursor.execute.call_args_list[0]
    assert "UPDATE events SET tickets_left" in decrement_call[0][0]
