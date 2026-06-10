from flask import Blueprint
from app.controlers.event_control import EventController

class EventRoutes:
    def __init__(self):
        self.bp = Blueprint("event", __name__)
        self.controller = EventController()

    def register(self):
        c = self.controller
        
        self.bp.route("/events", methods=["GET"])(c.events_page)
        self.bp.route("/events/<int:event_id>", methods=["GET"])(c.event_detail_page)
        self.bp.route("/api/events", methods=["GET"])(c.api_get_events)
        self.bp.route("/api/events/book", methods=["POST"])(c.api_book_event)
        
        return self.bp
 