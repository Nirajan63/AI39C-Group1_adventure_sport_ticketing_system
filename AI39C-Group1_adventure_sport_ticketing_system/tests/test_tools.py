"""
Tests for app/chatbot/tools.py.

Covers every function:
  - _find_static_activity
  - search_activities (a @tool - tested via its .func)
  - lookup_price (@tool)
  - check_availability (@tool)
  - lookup_weather (@tool)
  - build_booking_lookup_tool / lookup_my_bookings
  - search_faq (@tool)
  - build_tools

Note: functions decorated with @tool from langchain_core.tools are wrapped
into Tool objects. We call the original function via `.func(...)` so we can
test the underlying business logic directly, the same way the real
langchain StructuredTool exposes the wrapped callable.
"""
import pytest
from unittest.mock import patch, MagicMock

from app.chatbot import tools


# ── _find_static_activity ────────────────────────────────────────────────
def test_find_static_activity_matches_by_key():
    key, act = tools._find_static_activity("paragliding")
    assert key == "paragliding"
    assert act["name"] == "Paragliding"


def test_find_static_activity_matches_by_name_substring():
    key, act = tools._find_static_activity("bungee jumping")
    assert key == "bungee"


def test_find_static_activity_no_match_returns_none_none():
    key, act = tools._find_static_activity("scuba diving")
    assert key is None
    assert act is None


# ── search_activities ────────────────────────────────────────────────────
@patch("app.chatbot.tools.get_published_events")
@patch("app.chatbot.tools.get_db_connection")
def test_search_activities_finds_static_activity(mock_get_db, mock_get_published):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_get_db.return_value = mock_conn
    mock_get_published.return_value = {"events": []}

    result = tools.search_activities.func("paragliding")

    assert "Paragliding" in result
    assert "NPR 4500.0" in result


@patch("app.chatbot.tools.get_published_events")
@patch("app.chatbot.tools.get_db_connection")
def test_search_activities_no_matches_returns_helpful_message(mock_get_db, mock_get_published):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_get_db.return_value = mock_conn
    mock_get_published.return_value = {"events": []}

    result = tools.search_activities.func("xyznonexistent")

    assert "No activities or events found" in result


@patch("app.chatbot.tools.get_published_events")
@patch("app.chatbot.tools.get_db_connection", side_effect=Exception("db down"))
def test_search_activities_db_error_is_caught(mock_get_db, mock_get_published):
    mock_get_published.return_value = {"events": []}

    # Should not raise even though the DB lookup fails; static results still work.
    result = tools.search_activities.func("paragliding")
    assert "Paragliding" in result


# ── lookup_price ─────────────────────────────────────────────────────────
def test_lookup_price_static_activity():
    result = tools.lookup_price.func("Paragliding")
    assert result == "Paragliding costs NPR 4500.0 per person."


@patch("app.chatbot.tools.get_published_events")
@patch("app.chatbot.tools.get_db_connection")
def test_lookup_price_db_activity_match(mock_get_db, mock_get_published):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"name": "Heli Skiing", "price": 25000}
    mock_get_db.return_value = mock_conn

    result = tools.lookup_price.func("heli skiing")

    assert "Heli Skiing costs NPR 25000" in result


@patch("app.chatbot.tools.get_published_events")
@patch("app.chatbot.tools.get_db_connection")
def test_lookup_price_event_match(mock_get_db, mock_get_published):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_get_db.return_value = mock_conn
    mock_get_published.return_value = {"events": [{"title": "Jazz Night", "price": 800}]}

    result = tools.lookup_price.func("jazz night")

    assert "Jazz Night costs NPR 800" in result


@patch("app.chatbot.tools.get_published_events")
@patch("app.chatbot.tools.get_db_connection")
def test_lookup_price_no_match(mock_get_db, mock_get_published):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_get_db.return_value = mock_conn
    mock_get_published.return_value = {"events": []}

    result = tools.lookup_price.func("nonexistent activity")

    assert "couldn't find pricing" in result


# ── check_availability ───────────────────────────────────────────────────
@patch("app.chatbot.tools.get_db_connection")
def test_check_availability_static_activity_has_room(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"booked": 2}
    mock_get_db.return_value = mock_conn

    result = tools.check_availability.func("paragliding", "2026-07-01")

    assert "spot(s) available" in result


@patch("app.chatbot.tools.get_db_connection")
def test_check_availability_static_activity_fully_booked(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"booked": 10}  # equals capacity for paragliding
    mock_get_db.return_value = mock_conn

    result = tools.check_availability.func("paragliding", "2026-07-01")

    assert "fully booked" in result


@patch("app.chatbot.tools.get_db_connection")
def test_check_availability_static_activity_almost_sold_out(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"booked": 8}  # 2 remaining of 10
    mock_get_db.return_value = mock_conn

    result = tools.check_availability.func("paragliding", "2026-07-01")

    assert "almost sold out" in result


@patch("app.chatbot.tools.get_db_connection")
def test_check_availability_static_activity_db_error(mock_get_db):
    mock_get_db.side_effect = Exception("db down")

    result = tools.check_availability.func("paragliding", "2026-07-01")

    assert "couldn't check live availability" in result


@patch("app.chatbot.tools.get_db_connection")
def test_check_availability_event_match(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"id": 1, "title": "Jazz Night", "tickets_left": 4}
    mock_get_db.return_value = mock_conn

    result = tools.check_availability.func("jazz night", "2026-07-10")

    assert "only 4 ticket(s) left" in result


@patch("app.chatbot.tools.get_db_connection")
def test_check_availability_no_match(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_get_db.return_value = mock_conn

    result = tools.check_availability.func("nonexistent", "2026-07-10")

    assert "couldn't find" in result


# ── lookup_weather ───────────────────────────────────────────────────────
@patch("app.chatbot.tools.requests.get")
def test_lookup_weather_success(mock_get):
    geo_response = MagicMock()
    geo_response.json.return_value = {
        "results": [{"latitude": 28.2, "longitude": 83.9, "name": "Pokhara"}]
    }
    weather_response = MagicMock()
    weather_response.json.return_value = {"current_weather": {"temperature": 22, "windspeed": 5}}
    mock_get.side_effect = [geo_response, weather_response]

    result = tools.lookup_weather.func("Pokhara")

    assert "Pokhara" in result
    assert "22" in result


@patch("app.chatbot.tools.requests.get")
def test_lookup_weather_location_not_found(mock_get):
    geo_response = MagicMock()
    geo_response.json.return_value = {"results": []}
    mock_get.return_value = geo_response

    result = tools.lookup_weather.func("Nowhereville")

    assert "couldn't find weather data" in result


@patch("app.chatbot.tools.requests.get", side_effect=Exception("network error"))
def test_lookup_weather_network_error(mock_get):
    result = tools.lookup_weather.func("Pokhara")
    assert "couldn't fetch live weather" in result


# ── build_booking_lookup_tool / lookup_my_bookings ───────────────────────
def test_build_booking_lookup_tool_not_logged_in():
    lookup = tools.build_booking_lookup_tool(None)
    result = lookup.func()
    assert "isn't logged in" in result


@patch("app.chatbot.tools.get_db_connection")
def test_build_booking_lookup_tool_no_bookings(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_get_db.return_value = mock_conn

    lookup = tools.build_booking_lookup_tool(1)
    result = lookup.func()

    assert "no bookings yet" in result


@patch("app.chatbot.tools.get_db_connection")
def test_build_booking_lookup_tool_with_bookings(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{
        "activity": "Paragliding", "date": "2026-07-01", "people": 2,
        "total": 9000, "status": "confirmed", "payment_status": "confirmed"
    }]
    mock_get_db.return_value = mock_conn

    lookup = tools.build_booking_lookup_tool(1)
    result = lookup.func()

    assert "Paragliding" in result
    assert "NPR 9000" in result


@patch("app.chatbot.tools.get_db_connection", side_effect=Exception("db down"))
def test_build_booking_lookup_tool_db_error(mock_get_db):
    lookup = tools.build_booking_lookup_tool(1)
    result = lookup.func()
    assert "couldn't look up bookings" in result


# ── search_faq ───────────────────────────────────────────────────────────
def test_search_faq_returns_joined_content():
    fake_results = [{"content": "Q: A?\nA: B."}, {"content": "Q: C?\nA: D."}]
    with patch("app.chatbot.faiss_store.search_faq", return_value=fake_results):
        result = tools.search_faq.func("cancel booking")

    assert "Q: A?\nA: B." in result
    assert "Q: C?\nA: D." in result


def test_search_faq_no_results():
    with patch("app.chatbot.faiss_store.search_faq", return_value=[]):
        result = tools.search_faq.func("totally unrelated gibberish")

    assert result == "No matching FAQ entry found."


def test_search_faq_handles_internal_error():
    with patch("app.chatbot.faiss_store.search_faq", side_effect=Exception("index error")):
        result = tools.search_faq.func("cancel booking")

    assert "couldn't search the FAQ" in result


# ── build_tools ──────────────────────────────────────────────────────────
def test_build_tools_returns_six_tools():
    result = tools.build_tools(user_id=1)
    assert len(result) == 6


def test_build_tools_defaults_user_id_to_none():
    result = tools.build_tools()
    assert len(result) == 6
    # last tool is the booking lookup tool, bound to user_id=None
    booking_tool = result[-1]
    assert "isn't logged in" in booking_tool.func()
