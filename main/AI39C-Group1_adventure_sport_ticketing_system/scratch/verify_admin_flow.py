import requests

def main():
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()

    # 1. Access login page
    print("Accessing login page...")
    r = session.get(f"{base_url}/admin/login")
    if r.status_code != 200:
        print(f"[ERROR] Failed to access login page: {r.status_code}")
        return

    # Extract CSRF token if present in cookies or HTML (noting standard Flask configurations)
    csrf_token = session.cookies.get("csrf_token", "")
    print(f"CSRF cookie: {csrf_token}")

    # 2. Attempt login
    print("Attempting admin login...")
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    r = session.post(f"{base_url}/admin/login", data=payload, allow_redirects=False)
    print(f"Login Response: Status Code {r.status_code}, Headers: {dict(r.headers)}")
    
    if r.status_code not in [302, 200]:
        print("[ERROR] Login failed!")
        return

    import re

    # Follow redirect
    csrf_token_extracted = ""
    redirect_url = r.headers.get("Location")
    if redirect_url:
        print(f"Following redirect to: {redirect_url}")
        if not redirect_url.startswith("http"):
            redirect_url = base_url + redirect_url
        r = session.get(redirect_url)
        print(f"Redirect page status: {r.status_code}")
        
        # Search for window.CSRF_TOKEN
        match = re.search(r'window\.CSRF_TOKEN\s*=\s*"([^"]+)"', r.text)
        if match:
            csrf_token_extracted = match.group(1)
            print(f"[OK] Extracted CSRF token: {csrf_token_extracted}")
            
        if "Dashboard Overview" in r.text:
            print("[OK] Logged in successfully and reached Admin Dashboard Overview!")
        else:
            print("[WARNING] Reached dashboard route but 'Dashboard Overview' not found in HTML.")

    # 3. Retrieve events list
    print("Fetching events from API...")
    r = session.get(f"{base_url}/admin/api/events")
    print(f"Events GET status: {r.status_code}")
    if r.status_code == 200:
        events = r.json()
        print(f"[OK] Fetched {len(events)} events.")
        print(events)
    else:
        print(f"[ERROR] Failed to fetch events: {r.text}")
        return

    # 4. Create an event
    print("Creating a new test event...")
    event_payload = {
        "title": "Automated Test Event",
        "category": "Adventure",
        "price": 5000,
        "tickets_left": 30,
        "location": "Pokhara",
        "duration": "2 Hours",
        "date_time": "2026-08-20T10:00",
        "badge": "New",
        "image_url": "Mountain-Main.png",
        "is_published": 1,
        "description": "Created by automated validation script."
    }
    
    # Check for CSRF headers
    headers = {}
    if csrf_token_extracted:
        headers["X-CSRF-Token"] = csrf_token_extracted

    r = session.post(f"{base_url}/admin/api/events", json=event_payload, headers=headers)
    print(f"Event creation response: {r.status_code}")
    created_event_id = None
    if r.status_code == 200:
        res_json = r.json()
        print("[OK] Event creation response JSON:", res_json)
        if res_json.get("success"):
            # Refetch events to find the created event
            r_events = session.get(f"{base_url}/admin/api/events")
            if r_events.status_code == 200:
                events = r_events.json()
                for e in events:
                    if e["title"] == "Automated Test Event":
                        created_event_id = e["id"]
                        print(f"[OK] Found created test event with ID: {created_event_id}")
                        break
    else:
        print(f"[ERROR] Failed to create event: {r.text}")
        return

    if not created_event_id:
        print("[ERROR] Test event was not found in the list after creation.")
        return

    # 5. Dispatch a test notification
    print("Dispatching test notification...")
    notif_payload = {
        "target_type": "all",
        "target_id": "",
        "title": "Automated Broadcast",
        "message": "This is a broadcast alert sent from our verification script."
    }
    r = session.post(f"{base_url}/admin/api/notifications", json=notif_payload, headers=headers)
    print(f"Notification dispatch response: {r.status_code}")
    if r.status_code == 200:
        print("[OK] Notification response JSON:", r.json())
    else:
        print(f"[ERROR] Notification dispatch failed: {r.text}")

    # 6. Delete/Cancel the test event
    print(f"Cancelling and deleting test event #{created_event_id}...")
    r = session.delete(f"{base_url}/admin/api/events/{created_event_id}", headers=headers)
    print(f"Delete event response: {r.status_code}")
    if r.status_code == 200:
        print("[OK] Delete response JSON:", r.json())
    else:
        print(f"[ERROR] Delete event failed: {r.text}")

    print("Verification completed successfully!")

if __name__ == '__main__':
    main()
