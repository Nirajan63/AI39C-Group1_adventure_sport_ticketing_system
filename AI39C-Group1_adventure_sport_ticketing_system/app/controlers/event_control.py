from flask import render_template, request, jsonify, session, url_for, redirect, flash
from app.models.database import (
    get_published_events,
    get_featured_events,
    get_distinct_categories,
    get_distinct_locations,
    get_event_by_id,
    create_booking
)
from app.controlers.baseController import BaseController

class EventController(BaseController):
    def events_page(self):
        # Fetch wishlist count for badge if logged in
        wishlist_count = 0
        user = session.get("user")
        if user:
            from app.models.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?", (user["id"],))
            row = cursor.fetchone()
            wishlist_count = row["count"] if row else 0
            conn.close()

        categories = get_distinct_categories()
        locations = get_distinct_locations()
        featured = get_featured_events()
        initial_data = get_published_events({}, page=1, per_page=6)
        
        return render_template(
            "events.html",
            user=user,
            wishlist_count=wishlist_count,
            categories=categories,
            locations=locations,
            featured_events=featured,
            events=initial_data["events"],
            pagination=initial_data
        )

    def event_detail_page(self, event_id):
        user = session.get("user")
        # Fetch wishlist count for badge
        wishlist_count = 0
        if user:
            from app.models.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?", (user["id"],))
            row = cursor.fetchone()
            wishlist_count = row["count"] if row else 0
            conn.close()

        event = get_event_by_id(event_id)
        if not event:
            flash("Event not found.", "error")
            return redirect(url_for("event.events_page"))
            
        event_dict = dict(event)
        return render_template(
            "event_detail.html",
            user=user,
            wishlist_count=wishlist_count,
            event=event_dict
        )

    def api_get_events(self):
        filters = {
            "category": request.args.get("category"),
            "location": request.args.get("location"),
            "search": request.args.get("search"),
            "date_start": request.args.get("date_start"),
            "date_end": request.args.get("date_end"),
            "price_max": request.args.get("price_max"),
            "sort_by": request.args.get("sort_by")
        }
        
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 6, type=int)
        
        result = get_published_events(filters, page=page, per_page=per_page)
        return jsonify(result)

    def api_book_event(self):
        user = session.get("user")
        if not user:
            return jsonify({"status": "error", "message": "Please login to book events."}), 401
            
        data = request.get_json(silent=True) or {}
        event_id = data.get("event_id")
        booking_date = data.get("date")
        people = data.get("people", 1)
        
        if not event_id or not booking_date:
            return jsonify({"status": "error", "message": "Missing event ID or booking date."}), 400
            
        booking_id = create_booking(user["id"], f"event_{event_id}", booking_date, people)
        if not booking_id:
            return jsonify({"status": "error", "message": "Failed to book event. It might be sold out or unavailable."}), 400
            
        return jsonify({
            "status": "success",
            "message": "Event booked successfully!",
            "booking_id": booking_id,
            "redirect": "/dashboard#bookings"
        })
