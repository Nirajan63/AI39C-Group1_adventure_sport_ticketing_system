import requests
import re
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_workflow():
    print("=== STARTING NOTIFICATIONS SYSTEM INTEGRATION TEST ===")
    
    # 1. Start session for Test User
    user_sess = requests.Session()
    print("\n1. Logging in as testuser...")
    login_resp = user_sess.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "password123"})
    if login_resp.status_code != 200:
        print(f"FAILED: Could not login as testuser. Status: {login_resp.status_code}")
        print(login_resp.text)
        sys.exit(1)
    print("SUCCESS: Logged in as testuser!")
    
    # 2. Get current notifications for testuser
    print("\n2. Getting notifications for testuser...")
    notifs_resp = user_sess.get(f"{BASE_URL}/api/notifications")
    if notifs_resp.status_code != 200:
        print(f"FAILED: Could not get notifications. Status: {notifs_resp.status_code}")
        sys.exit(1)
    initial_notifs = notifs_resp.json()
    print(f"SUCCESS: Retrieved {len(initial_notifs)} notifications.")

    # 2.5 Test Booking Confirmation Notification
    print("\n2.5. Booking a standard activity ('paragliding') for testuser...")
    book_data = {
        "activity_id": "paragliding",
        "date": "2026-07-20",
        "people": "2",
        "payment_method": "qr",
        "txn_code": "TXN-AUTO-998877"
    }
    book_resp = user_sess.post(f"{BASE_URL}/book", data=book_data)
    if book_resp.status_code != 200 and "dashboard" not in book_resp.url:
        print(f"FAILED: Booking request failed. Status: {book_resp.status_code}")
        sys.exit(1)
    print("SUCCESS: Booked activity!")

    # Fetch notifications to verify booking confirmation
    notifs_after_booking = user_sess.get(f"{BASE_URL}/api/notifications").json()
    booking_notif = next((n for n in notifs_after_booking if n["title"] == "Booking Confirmed" and "paragliding" in n["message"].lower()), None)
    if not booking_notif:
        print("FAILED: No booking confirmation notification received!")
        sys.exit(1)
    print(f"SUCCESS: Received booking confirmation notification: '{booking_notif['message']}'")
    
    # 3. Start session for Admin
    admin_sess = requests.Session()
    print("\n3. Logging in as admin...")
    admin_login_resp = admin_sess.post(f"{BASE_URL}/admin/login", data={"username": "admin", "password": "admin123"}, allow_redirects=True)
    if "Invalid credentials" in admin_login_resp.text:
        print("FAILED: Invalid credentials for admin login.")
        sys.exit(1)
    print("SUCCESS: Logged in as admin!")
    
    # 4. Fetch admin dashboard to extract CSRF Token
    print("\n4. Fetching admin dashboard for CSRF token...")
    dash_resp = admin_sess.get(f"{BASE_URL}/admin/dashboard")
    csrf_match = re.search(r'window\.CSRF_TOKEN = "([^"]+)";', dash_resp.text)
    if not csrf_match:
        print("FAILED: Could not extract CSRF token from dashboard.")
        sys.exit(1)
    csrf_token = csrf_match.group(1)
    print(f"SUCCESS: Extracted CSRF token: {csrf_token[:8]}...")
    
    # We will pass this CSRF token in headers for admin POST/PUT/DELETE requests
    admin_headers = {
        "X-CSRF-Token": csrf_token,
        "Content-Type": "application/json"
    }
    
    # 5. Create an event as Admin
    print("\n5. Creating a test event as admin...")
    event_data = {
        "title": "Super Paragliding Flyoff",
        "description": "High altitude paragliding championship",
        "date_time": "2026-07-15T09:00:00",
        "location": "Pokhara",
        "category": "Sky",
        "price": 5000,
        "tickets_left": 30,
        "image_url": "Paragliding.png",
        "badge": "Championship",
        "duration": "4 hours",
        "is_published": 1
    }
    create_evt_resp = admin_sess.post(f"{BASE_URL}/admin/api/events", json=event_data, headers=admin_headers)
    if create_evt_resp.status_code != 200:
        print(f"FAILED: Event creation failed. Status: {create_evt_resp.status_code}")
        print(create_evt_resp.text)
        sys.exit(1)
    print("SUCCESS: Created event successfully!")
    
    # Fetch events list to get the event ID
    events_list_resp = admin_sess.get(f"{BASE_URL}/admin/api/events")
    events = events_list_resp.json()
    new_event = next((e for e in events if e["title"] == "Super Paragliding Flyoff"), None)
    if not new_event:
        print("FAILED: New event not found in events list.")
        sys.exit(1)
    event_id = new_event["id"]
    event_key = f"event_{event_id}"
    print(f"SUCCESS: Event ID is {event_id} (key: {event_key})")
    
    # 6. Wishlist the event as testuser
    print(f"\n6. Wishlisting event '{event_key}' as testuser...")
    wishlist_resp = user_sess.post(f"{BASE_URL}/api/wishlist/toggle", json={"activity_id": event_key})
    if wishlist_resp.status_code != 200:
        print(f"FAILED: Wishlist toggle failed. Status: {wishlist_resp.status_code}")
        print(wishlist_resp.text)
        sys.exit(1)
    print("SUCCESS: Wishlist toggled!")
    
    # 7. Send event-specific notification as Admin
    print(f"\n7. Sending targeted event notification for {event_key} as admin...")
    notif_data = {
        "target_type": "event",
        "target_id": event_key,
        "title": "Flyoff Briefing Update",
        "message": "The weather forecast is clear. Briefing starts 30 mins early!"
    }
    evt_notif_resp = admin_sess.post(f"{BASE_URL}/admin/api/notifications", json=notif_data, headers=admin_headers)
    if evt_notif_resp.status_code != 200:
        print(f"FAILED: Event notification send failed. Status: {evt_notif_resp.status_code}")
        print(evt_notif_resp.text)
        sys.exit(1)
    print("SUCCESS: Event-specific notification sent!")
    
    # 8. Verify testuser received the event notification
    print("\n8. Verifying testuser received the notification...")
    user_notifs_resp = user_sess.get(f"{BASE_URL}/api/notifications")
    user_notifs = user_notifs_resp.json()
    matched_notif = next((n for n in user_notifs if n["title"] == "Flyoff Briefing Update"), None)
    if not matched_notif:
        print("FAILED: testuser did not receive the event notification!")
        sys.exit(1)
    print(f"SUCCESS: testuser received notification: '{matched_notif['message']}'")
    
    # 9. Mark individual notification as read
    notif_id = matched_notif["id"]
    print(f"\n9. Marking notification {notif_id} as read...")
    read_resp = user_sess.post(f"{BASE_URL}/read-notification", json={"id": notif_id})
    if read_resp.status_code != 200 or not read_resp.json().get("success"):
        print(f"FAILED: Marking read failed. Status: {read_resp.status_code}")
        sys.exit(1)
    print("SUCCESS: Notification marked as read!")
    
    # Verify status changed
    verify_read_resp = user_sess.get(f"{BASE_URL}/api/notifications")
    updated_notif = next((n for n in verify_read_resp.json() if n["id"] == notif_id), None)
    if not updated_notif or updated_notif["status"] != "read":
        print("FAILED: Notification status is not 'read'!")
        sys.exit(1)
    print("SUCCESS: Confirmed notification status is 'read'.")
    
    # 10. Update the event details as Admin
    print("\n10. Updating event details as admin...")
    update_data = {
        "title": "Super Paragliding Flyoff",
        "description": "High altitude paragliding championship - Edited",
        "date_time": "2026-07-15T08:30:00", # Changed time
        "location": "Pokhara - West Hill",   # Changed location
        "category": "Sky",
        "price": 5000,
        "tickets_left": 30,
        "image_url": "Paragliding.png",
        "badge": "Championship",
        "duration": "4 hours",
        "is_published": 1
    }
    update_resp = admin_sess.put(f"{BASE_URL}/admin/api/events/{event_id}", json=update_data, headers=admin_headers)
    if update_resp.status_code != 200:
        print(f"FAILED: Event update failed. Status: {update_resp.status_code}")
        sys.exit(1)
    print("SUCCESS: Event updated successfully!")
    
    # Verify testuser receives update notification
    print("\n11. Verifying testuser received update notification...")
    user_notifs_resp = user_sess.get(f"{BASE_URL}/api/notifications")
    update_notif = next((n for n in user_notifs_resp.json() if "Event Updated" in n["title"]), None)
    if not update_notif:
        print("FAILED: testuser did not receive the update notification!")
        sys.exit(1)
    print(f"SUCCESS: testuser received update: '{update_notif['message']}'")
    
    # 12. Cancel the event (Delete) as Admin
    print("\n12. Cancelling (deleting) event as admin...")
    cancel_resp = admin_sess.delete(f"{BASE_URL}/admin/api/events/{event_id}", headers=admin_headers)
    if cancel_resp.status_code != 200:
        print(f"FAILED: Event cancellation failed. Status: {cancel_resp.status_code}")
        print(cancel_resp.text)
        sys.exit(1)
    print("SUCCESS: Cancel response:", cancel_resp.json()["message"])
    
    # Verify testuser receives cancellation notification
    print("\n13. Verifying testuser received cancellation notification...")
    user_notifs_resp = user_sess.get(f"{BASE_URL}/api/notifications")
    cancel_notif = next((n for n in user_notifs_resp.json() if "Event Cancelled" in n["title"]), None)
    if not cancel_notif:
        print("FAILED: testuser did not receive cancellation notification!")
        sys.exit(1)
    print(f"SUCCESS: testuser received cancellation: '{cancel_notif['message']}'")
    
    # 14. Mark all notifications as read
    print("\n14. Marking all notifications as read for testuser...")
    read_all_resp = user_sess.post(f"{BASE_URL}/api/notifications/read-all")
    if read_all_resp.status_code != 200 or not read_all_resp.json().get("success"):
        print(f"FAILED: Mark all read failed. Status: {read_all_resp.status_code}")
        sys.exit(1)
    print("SUCCESS: All notifications marked as read!")
    
    # Verify all are read
    final_notifs_resp = user_sess.get(f"{BASE_URL}/api/notifications")
    unread_count = sum(1 for n in final_notifs_resp.json() if n["status"] == "unread")
    if unread_count > 0:
        print(f"FAILED: Found {unread_count} unread notifications after read-all!")
        sys.exit(1)
    print("SUCCESS: Confirmed 0 unread notifications!")
    
    print("\n=== ALL SYSTEM TESTS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_workflow()
