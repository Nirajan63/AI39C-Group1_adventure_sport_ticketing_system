# app/chatbot/tools.py
"""
LangChain tool layer for the SportAdventure chatbot.

Each tool is a thin, read-only wrapper around the app's existing data
sources (the static ACTIVITIES dict, the `activities`/`events`/`bookings`
MySQL tables) so the agent can ground its answers in real, current data
instead of guessing.

IMPORTANT (security): build_tools() is called once per request, with the
logged-in user's id (or None) captured from the Flask session by the route
handler -- never by the model. The booking-lookup tool closes over that
value, so the LLM can never read another user's bookings by passing a
different id as an argument; it can only ask "look up bookings", and the
tool always answers for whoever is actually logged in.
"""

import requests
from langchain_core.tools import tool

from app.controlers.auth_control import ACTIVITIES
from app.models.database import (
    get_db_connection,
    get_event_by_id,
    get_published_events,
)

# Mirrors the CAPACITIES dict used by the dashboard's availability calculation
# (auth_control.py) for the six static legacy activities.
STATIC_CAPACITIES = {
    "paragliding": 10,
    "bungee jumping": 15,
    "white water rafting": 20,
    "trekking": 15,
    "canyoning": 10,
    "zip-lining": 20,
}


def _find_static_activity(name: str):
    name_l = name.strip().lower()
    for key, act in ACTIVITIES.items():
        if name_l == key.lower() or name_l in act["name"].lower():
            return key, act
    return None, None


@tool
def search_activities(query: str) -> str:
    """
    Search for adventure activities and events by name, category, or location
    keyword (e.g. "paragliding", "rafting in Trishuli", "trekking"). Returns
    a short list of matches with their type (activity/event), price, and
    location. Use this first whenever a user asks what is offered or
    mentions an activity by name.
    """
    query_l = query.strip().lower()
    matches = []

    for key, act in ACTIVITIES.items():
        if query_l in key.lower() or query_l in act["name"].lower() or query_l in act.get("location", "").lower():
            matches.append(f"- {act['name']} (activity) - NPR {act['price']} - {act['location']} - {act.get('duration', 'N/A')}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, price, location, category FROM activities "
            "WHERE status = 'active' AND (LOWER(name) LIKE %s OR LOWER(location) LIKE %s OR LOWER(category) LIKE %s)",
            (f"%{query_l}%", f"%{query_l}%", f"%{query_l}%"),
        )
        for row in cursor.fetchall():
            matches.append(f"- {row['name']} (activity) - NPR {row['price']} - {row['location']}")
        conn.close()
    except Exception as e:
        print(f"[chatbot tool] search_activities DB error: {e}", flush=True)

    try:
        result = get_published_events({"search": query}, page=1, per_page=5)
        for ev in result.get("events", []):
            matches.append(
                f"- {ev['title']} (event) - NPR {ev['price']} - {ev['location']} - "
                f"on {ev.get('date_time', 'TBA')} - {ev.get('tickets_left', '?')} tickets left"
            )
    except Exception as e:
        print(f"[chatbot tool] search_activities events error: {e}", flush=True)

    if not matches:
        return f"No activities or events found matching '{query}'. Try a broader term like 'trekking' or 'rafting'."

    seen = set()
    deduped = [m for m in matches if not (m in seen or seen.add(m))]
    return "\n".join(deduped[:8])


@tool
def lookup_price(activity_name: str) -> str:
    """
    Look up the price of a specific activity or event by name
    (e.g. "Paragliding", "Bungee Jumping", "Annapurna Base Camp Trek").
    Returns the price in NPR, or says if nothing matched.
    """
    key, act = _find_static_activity(activity_name)
    if act:
        return f"{act['name']} costs NPR {act['price']} per person."

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, price FROM activities WHERE status = 'active' AND LOWER(name) LIKE %s LIMIT 1",
            (f"%{activity_name.strip().lower()}%",),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return f"{row['name']} costs NPR {row['price']} per person."
    except Exception as e:
        print(f"[chatbot tool] lookup_price DB error: {e}", flush=True)

    try:
        result = get_published_events({"search": activity_name}, page=1, per_page=1)
        events = result.get("events", [])
        if events:
            ev = events[0]
            return f"{ev['title']} costs NPR {ev['price']} per person."
    except Exception as e:
        print(f"[chatbot tool] lookup_price events error: {e}", flush=True)

    return f"I couldn't find pricing for '{activity_name}'. Could you check the spelling or try a different activity name?"


@tool
def check_availability(activity_name: str, date: str) -> str:
    """
    Check how many slots/tickets remain for a given activity or event on a
    specific date. `date` must be in YYYY-MM-DD format. Use this when a user
    asks if a date is available or sold out.
    """
    key, act = _find_static_activity(activity_name)
    if act:
        capacity = STATIC_CAPACITIES.get(key, 10)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(SUM(people), 0) AS booked FROM bookings "
                "WHERE activity = ? AND date = ? AND status != 'cancelled'",
                (act["name"], date),
            )
            booked = cursor.fetchone()["booked"] or 0
            conn.close()
            remaining = max(capacity - booked, 0)
            if remaining == 0:
                return f"{act['name']} is fully booked on {date}. Try a nearby date instead."
            elif remaining <= 3:
                return f"{act['name']} has only {remaining} spot(s) left on {date} -- almost sold out."
            return f"{act['name']} has {remaining} spot(s) available on {date}."
        except Exception as e:
            print(f"[chatbot tool] check_availability DB error: {e}", flush=True)
            return "I couldn't check live availability right now, please try again shortly."

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, tickets_left FROM events WHERE LOWER(title) LIKE %s AND is_published = 1 LIMIT 1",
            (f"%{activity_name.strip().lower()}%",),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            tickets = row["tickets_left"]
            if tickets <= 0:
                return f"{row['title']} is sold out."
            elif tickets <= 5:
                return f"{row['title']} has only {tickets} ticket(s) left."
            return f"{row['title']} has {tickets} ticket(s) available."
    except Exception as e:
        print(f"[chatbot tool] check_availability events error: {e}", flush=True)

    return f"I couldn't find '{activity_name}' to check availability. Could you confirm the exact activity or event name?"


@tool
def lookup_weather(location: str) -> str:
    """
    Get a short current-weather summary for a Nepal adventure location
    (e.g. "Pokhara", "Kathmandu", "Annapurna"). Useful when a user asks if
    conditions are good for an outdoor activity. Uses a free, no-API-key
    weather service.
    """
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    try:
        geo_resp = requests.get(geocode_url, params={"name": location, "count": 1}, timeout=6)
        geo_resp.raise_for_status()
        results = geo_resp.json().get("results")
        if not results:
            return f"I couldn't find weather data for '{location}'. Try a nearby major town instead."

        lat, lon = results[0]["latitude"], results[0]["longitude"]
        resolved_name = results[0].get("name", location)

        weather_resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "current_weather": "true"},
            timeout=6,
        )
        weather_resp.raise_for_status()
        current = weather_resp.json().get("current_weather", {})
        if not current:
            return f"Weather data for {resolved_name} is currently unavailable."

        temp = current.get("temperature")
        wind = current.get("windspeed")
        return (
            f"Current conditions in {resolved_name}: {temp}°C, wind speed {wind} km/h. "
            f"Always double-check conditions with your activity guide on the day, "
            f"since mountain weather can change quickly."
        )
    except Exception as e:
        print(f"[chatbot tool] lookup_weather error: {e}", flush=True)
        return f"I couldn't fetch live weather for '{location}' right now."


def build_booking_lookup_tool(user_id):
    """
    Factory: returns a booking-lookup tool bound to a specific user_id,
    captured from the Flask session by the route handler (never from the
    model). If user_id is None (not logged in), the tool tells the user to
    log in instead of querying the database.
    """

    @tool
    def lookup_my_bookings() -> str:
        """
        Look up the current logged-in user's own bookings (status, activity,
        date, payment status). Takes no input -- always returns the caller's
        own bookings, never another user's. Use this whenever the user asks
        about "my booking", "my reservation", or their booking/payment status.
        """
        if not user_id:
            return "This user isn't logged in, so I can't look up bookings. Ask them to log in first, then ask again."

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT activity, date, people, total, status, payment_status "
                "FROM bookings WHERE user_id = ? ORDER BY id DESC LIMIT 10",
                (user_id,),
            )
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            print(f"[chatbot tool] lookup_my_bookings DB error: {e}", flush=True)
            return "I couldn't look up bookings right now, please try again shortly."

        if not rows:
            return "This user has no bookings yet."

        lines = []
        for r in rows:
            lines.append(
                f"- {r['activity']} on {r['date']} for {r['people']} people - "
                f"NPR {r['total']} - status: {r['status']} - payment: {r['payment_status']}"
            )
        return "\n".join(lines)

    return lookup_my_bookings


@tool
def search_faq(query: str) -> str:
    """
    Search the site's FAQ knowledge base for policy/how-to questions, e.g.
    "how do I cancel a booking", "what payment methods are accepted",
    "how do refunds work", "is it safe". Use this for general policy and
    how-to questions rather than questions about specific live prices or
    dates.
    """
    from app.chatbot.faiss_store import search_faq as _search_faq

    try:
        results = _search_faq(query, k=3)
    except Exception as e:
        print(f"[chatbot tool] search_faq error: {e}", flush=True)
        return "I couldn't search the FAQ right now."

    if not results:
        return "No matching FAQ entry found."

    return "\n\n".join(r["content"] for r in results)


def build_tools(user_id=None):
    """Returns the full tool list for one request, scoped to user_id."""
    return [
        search_activities,
        lookup_price,
        check_availability,
        lookup_weather,
        search_faq,
        build_booking_lookup_tool(user_id),
    ]
