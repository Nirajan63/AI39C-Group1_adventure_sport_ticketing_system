"""
Tests for app/controlers/event_control.py (EventController).

Covers every method:
  - events_page
  - event_detail_page
  - api_get_events
  - api_book_event

Note: get_db_connection is imported *locally inside each method* in the
real source (`from app.models.database import get_db_connection`), so the
correct patch target is app.models.database.get_db_connection, not the
event_control module namespace.
"""
import pytest
from flask import Flask
from unittest.mock import patch, MagicMock

from app.controlers.event_control import EventController

_app = Flask(__name__)


# ── events_page ──────────────────────────────────────────────────────────
@patch("app.controlers.event_control.render_template")
@patch("app.controlers.event_control.get_published_events")
@patch("app.controlers.event_control.get_featured_events")
@patch("app.controlers.event_control.get_distinct_locations")
@patch("app.controlers.event_control.get_distinct_categories")
@patch("app.models.database.get_db_connection")
def test_events_page_logged_in_user_includes_wishlist(
    mock_get_db, mock_categories, mock_locations, mock_featured, mock_published, mock_render
):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"count": 2}
    mock_cursor.fetchall.return_value = [{"activity_id": "paragliding"}]
    mock_get_db.return_value = mock_conn

    mock_categories.return_value = ["Adventure"]
    mock_locations.return_value = ["Pokhara"]
    mock_featured.return_value = []
    mock_published.return_value = {"events": [], "total_pages": 1}
    mock_render.return_value = "RENDERED"

    with _app.test_request_context():
        with patch("app.controlers.event_control.session", {"user": {"id": 1}}):
            controller = EventController()
            response = controller.events_page()

    assert response == "RENDERED"
    render_kwargs = mock_render.call_args[1]
    assert render_kwargs["wishlist_count"] == 2
    assert render_kwargs["user_wishlist_ids"] == ["paragliding"]


@patch("app.controlers.event_control.render_template")
@patch("app.controlers.event_control.get_published_events")
@patch("app.controlers.event_control.get_featured_events")
@patch("app.controlers.event_control.get_distinct_locations")
@patch("app.controlers.event_control.get_distinct_categories")
def test_events_page_anonymous_user_has_zero_wishlist(
    mock_categories, mock_locations, mock_featured, mock_published, mock_render
):
    mock_categories.return_value = []
    mock_locations.return_value = []
    mock_featured.return_value = []
    mock_published.return_value = {"events": [], "total_pages": 1}
    mock_render.return_value = "RENDERED"

    with _app.test_request_context():
        with patch("app.controlers.event_control.session", {}):
            controller = EventController()
            response = controller.events_page()

    render_kwargs = mock_render.call_args[1]
    assert render_kwargs["wishlist_count"] == 0
    assert render_kwargs["user_wishlist_ids"] == []
    assert response == "RENDERED"


# ── event_detail_page ───────────────────────────────────────────────────
@patch("app.controlers.event_control.render_template")
@patch("app.controlers.event_control.get_event_by_id")
@patch("app.models.database.get_db_connection")
def test_event_detail_page_found(mock_get_db, mock_get_event, mock_render):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"count": 0}
    mock_get_db.return_value = mock_conn
    mock_get_event.return_value = {"id": 5, "title": "Jazz Night"}
    mock_render.return_value = "RENDERED"

    with _app.test_request_context():
        with patch("app.controlers.event_control.session", {"user": {"id": 1}}):
            controller = EventController()
            response = controller.event_detail_page(5)

    assert response == "RENDERED"
    mock_get_event.assert_called_once_with(5)


@patch("app.controlers.event_control.flash")
@patch("app.controlers.event_control.redirect")
@patch("app.controlers.event_control.url_for")
@patch("app.controlers.event_control.get_event_by_id")
def test_event_detail_page_not_found_redirects(mock_get_event, mock_url_for, mock_redirect, mock_flash):
    mock_get_event.return_value = None
    mock_url_for.return_value = "/events"
    mock_redirect.return_value = "REDIRECT"

    with _app.test_request_context():
        with patch("app.controlers.event_control.session", {}):
            controller = EventController()
            response = controller.event_detail_page(999)

    mock_flash.assert_called_once()
    mock_url_for.assert_called_once_with("event.events_page")
    assert response == "REDIRECT"


# ── api_get_events ───────────────────────────────────────────────────────
@patch("app.controlers.event_control.jsonify")
@patch("app.controlers.event_control.get_published_events")
def test_api_get_events_passes_query_params_as_filters(mock_get_published, mock_jsonify):
    mock_get_published.return_value = {"events": [], "page": 1}
    mock_jsonify.side_effect = lambda x: x

    with _app.test_request_context(
        "/api/events?category=Adventure&location=Pokhara&search=raft"
        "&date_start=2026-01-01&date_end=2026-12-31&price_max=5000&sort_by=price_asc&page=2&per_page=3"
    ):
        controller = EventController()
        result = controller.api_get_events()

    filters_arg, kwargs = mock_get_published.call_args
    assert filters_arg[0]["category"] == "Adventure"
    assert filters_arg[0]["location"] == "Pokhara"
    assert filters_arg[0]["search"] == "raft"
    assert kwargs["page"] == 2
    assert kwargs["per_page"] == 3
    assert result == {"events": [], "page": 1}


@patch("app.controlers.event_control.jsonify")
@patch("app.controlers.event_control.get_published_events")
def test_api_get_events_defaults_page_and_per_page(mock_get_published, mock_jsonify):
    mock_get_published.return_value = {"events": []}
    mock_jsonify.side_effect = lambda x: x

    with _app.test_request_context("/api/events"):
        controller = EventController()
        controller.api_get_events()

    _, kwargs = mock_get_published.call_args
    assert kwargs["page"] == 1
    assert kwargs["per_page"] == 6


# ── api_book_event ───────────────────────────────────────────────────────
def test_api_book_event_unauthenticated_returns_401():
    with _app.test_request_context(method="POST", json={}):
        with patch("app.controlers.event_control.session", {}):
            controller = EventController()
            result, status = controller.api_book_event()

    assert status == 401
    assert result.json["status"] == "error"


def test_api_book_event_missing_fields_returns_400():
    with _app.test_request_context(method="POST", json={"people": 2}):
        with patch("app.controlers.event_control.session", {"user": {"id": 1}}):
            controller = EventController()
            result, status = controller.api_book_event()

    assert status == 400
    assert result.json["status"] == "error"


@patch("app.controlers.event_control.create_booking")
def test_api_book_event_booking_fails_returns_400(mock_create_booking):
    mock_create_booking.return_value = None

    with _app.test_request_context(
        method="POST", json={"event_id": 5, "date": "2026-07-01", "people": 2}
    ):
        with patch("app.controlers.event_control.session", {"user": {"id": 1}}):
            controller = EventController()
            result, status = controller.api_book_event()

    assert status == 400
    assert result.json["status"] == "error"


@patch("app.controlers.event_control.create_booking")
def test_api_book_event_success(mock_create_booking):
    mock_create_booking.return_value = 77

    with _app.test_request_context(
        method="POST", json={"event_id": 5, "date": "2026-07-01", "people": 2}
    ):
        with patch("app.controlers.event_control.session", {"user": {"id": 1}}):
            controller = EventController()
            result = controller.api_book_event()

    assert result.json["status"] == "success"
    assert result.json["booking_id"] == 77
    mock_create_booking.assert_called_once_with(1, "event_5", "2026-07-01", 2)


@patch("app.controlers.event_control.create_booking")
def test_api_book_event_defaults_people_to_one(mock_create_booking):
    mock_create_booking.return_value = 1

    with _app.test_request_context(method="POST", json={"event_id": 5, "date": "2026-07-01"}):
        with patch("app.controlers.event_control.session", {"user": {"id": 1}}):
            controller = EventController()
            controller.api_book_event()

    mock_create_booking.assert_called_once_with(1, "event_5", "2026-07-01", 1)
