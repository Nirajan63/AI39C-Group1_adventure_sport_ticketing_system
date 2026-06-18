from flask import render_template, request, session, redirect, url_for, flash, jsonify
import sqlite3
import random
import time
import os
from app.models.database import get_db_connection
from app.utils.email import send_email
from app.controlers.baseController import BaseController

# OTP Store for tracking validation codes in-memory (expires_at used for validation check)
otp_store = {}

# Activities Metadata Definition
ACTIVITIES = {
    "paragliding": {
        "id": "paragliding",
        "name": "Paragliding",
        "price": 4500.0,
        "location": "Pokhara",
        "duration": "1 hour",
        "img": "Paragliding.png",
        "pic": "Paragliding_Pic.jpg"
    },
    "bungee": {
        "id": "bungee",
        "name": "Bungee Jumping",
        "price": 6500.0,
        "location": "Bhote Koshi",
        "duration": "30 mins",
        "img": "Bungee-jumping.png",
        "pic": "BungeeJump_Pic.jpg"
    },
    "rafting": {
        "id": "rafting",
        "name": "White Water Rafting",
        "price": 3500.0,
        "location": "Trishuli",
        "duration": "4 hours",
        "img": "Rafting.png",
        "pic": "Rafting_Pic.jpg"
    },
    "trekking": {
        "id": "trekking",
        "name": "Trekking",
        "price": 2500.0,
        "location": "Annapurna",
        "duration": "2 days",
        "img": "Trekking_.png",
        "pic": "Trekking_Pic.jpeg"
    },
    "canyoning": {
        "id": "canyoning",
        "name": "Canyoning",
        "price": 5000.0,
        "location": "Jalbire",
        "duration": "5 hours",
        "img": "Canyoning.png",
        "pic": "Canyoning_Pic.jpg"
    },
    "ziplining": {
        "id": "ziplining",
        "name": "Zip-lining",
        "price": 2000.0,
        "location": "Chitwan",
        "duration": "2 hours",
        "img": "Zip_lining.png",
        "pic": "ZipLining_Pic.jpg"
    }
}


class AuthController(BaseController):

    # ── HOME ──────────────────────────────────────────────────────────────
    def home(self):
        # Determine current wishlist count to render badge
        wishlist_count = 0
        saved_wishlist = []
        user = session.get("user")
        if user:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?", (user["id"],))
            row = cursor.fetchone()
            if row:
                wishlist_count = row["count"]
            
            # Fetch saved activity IDs for pre-filling heart icons
            cursor.execute("SELECT activity_id FROM wishlist WHERE user_id = ?", (user["id"],))
            saved_wishlist = [w["activity_id"] for w in cursor.fetchall()]
            conn.close()
            
        return render_template("home.html", user=user, wishlist_count=wishlist_count, saved_wishlist=saved_wishlist)

    # ── PUBLIC ACTIVITY PAGE ────────────────────────────────────────────────
    def activity_page(self, activity_id):
        # Allow both logged in and non-logged in users
        user = session.get("user")
        wishlist_count = 0
        saved_wishlist = []
        if user:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?", (user["id"],))
            row = cursor.fetchone()
            if row:
                wishlist_count = row["count"]
            cursor.execute("SELECT activity_id FROM wishlist WHERE user_id = ?", (user["id"],))
            saved_wishlist = [w["activity_id"] for w in cursor.fetchall()]
            conn.close()

        act = ACTIVITIES.get(activity_id)
        # Check DB if not in static dict
        if not act:
            conn = get_db_connection()
            cursor = conn.cursor()
            db_act = cursor.execute("SELECT * FROM activities WHERE id = ?", (activity_id,)).fetchone()
            conn.close()
            if db_act:
                act = dict(db_act)
            else:
                flash("Activity not found.", "danger")
                return redirect(url_for("auth.home"))

        return render_template("activity.html", user=user, activity=act, wishlist_count=wishlist_count, saved_wishlist=saved_wishlist)

    # ── SEARCH SUGGESTIONS API ──────────────────────────────────────────────
    def api_search(self):
        query = request.args.get("q", "").strip().lower()
        if not query:
            return jsonify([])

        results = []
        # Search in static ACTIVITIES
        for key, act in ACTIVITIES.items():
            if query in act["name"].lower() or query in act.get("location", "").lower():
                results.append({
                    "id": act["id"],
                    "name": act["name"],
                    "category": act.get("category", "Adventure"),
                    "img": act["img"]
                })
        
        # Search in DB activities
        conn = get_db_connection()
        cursor = conn.cursor()
        db_results = cursor.execute("SELECT id, name, category, img FROM activities WHERE LOWER(name) LIKE ? OR LOWER(location) LIKE ?", (f"%{query}%", f"%{query}%")).fetchall()
        conn.close()

        for row in db_results:
            # Avoid duplicates
            if not any(r["id"] == row["id"] for r in results):
                results.append({
                    "id": row["id"],
                    "name": row["name"],
                    "category": row["category"],
                    "img": row["img"]
                })
                
        return jsonify(results)

    # ── LOGIN ──────────────────────────────────────────────────────────────
    def login(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            # Check if JSON request (submitted via AJAX)
            if request.is_json:
                data = request.json or {}
                username = data.get("username", "").strip()
                password = data.get("password", "")
            else:
                username = request.form.get("username", "").strip()
                password = request.form.get("password", "")

            if not username or not password:
                error_msg = "Username/Email and password are required."
                if request.is_json:
                    return jsonify({"message": error_msg, "status": "error"}), 400
                flash(error_msg, "danger")
                return render_template("login.html")

            # Check database for username OR email matching
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
            user_data = cursor.fetchone()
            conn.close()

            from werkzeug.security import check_password_hash
            is_valid_password = False
            if user_data:
                db_password = user_data["password"]
                if db_password == password:
                    is_valid_password = True
                elif db_password.startswith(("scrypt:", "pbkdf2:")) and check_password_hash(db_password, password):
                    is_valid_password = True

            if user_data and is_valid_password:
                if user_data.get("status") == "suspended":
                    error_msg = "Access denied: Your account has been suspended."
                    if request.is_json:
                        return jsonify({"message": error_msg, "status": "error"}), 403
                    flash(error_msg, "danger")
                    return render_template("login.html")

                # Store full user information in session
                session["user"] = {
                    "id": user_data["id"],
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "first_name": user_data["first_name"] or "",
                    "last_name": user_data["last_name"] or "",
                    "phone": user_data["phone"] or "",
                    "city": user_data["city"] or "",
                    "bio": user_data["bio"] or "",
                    "language": user_data["language"] or "en",
                    "role": user_data["role"] or "Adventure Seeker",
                    "avatar": user_data["avatar"] or "",
                    "cover": user_data["cover"] or "",
                    "theme_preference": user_data["theme_preference"] or "light",
                    "joined": "May 2026"
                }

                if request.is_json:
                    return jsonify({
                        "message": "Login successful!",
                        "status": "success",
                        "user": {"username": user_data["username"]}
                    }), 200
                
                return self.flash_and_redirect("Login successful!", "success", "auth.dashboard")

            # Failed Authentication
            error_msg = "Invalid username/email or password."
            if request.is_json:
                return jsonify({"message": error_msg, "status": "error"}), 400
            
            flash(error_msg, "danger")
            return render_template("login.html")

        return render_template("login.html")

    # ── REGISTER PAGE ──────────────────────────────────────────────────────
    def register_page(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))
        return render_template("register.html")

    # ── SIGNUP API ──────────────────────────────────────────────────────────
    @staticmethod
    def signup():
        data = request.json
        if not data:
            return jsonify({'message': 'Missing request body', 'status': 'error'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'message': 'All fields are required', 'status': 'error'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Username already exists', 'status': 'error'}), 400
            
        # Check if email exists
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Email already exists', 'status': 'error'}), 400
            
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                (username, email, password)
            )
            conn.commit()
        except Exception as e:
            conn.close()
            return jsonify({'message': f'Registration failed: {str(e)}', 'status': 'error'}), 500
        
        conn.close()
        return jsonify({'message': 'User registered successfully!', 'status': 'success'}), 201

    # ── LOGOUT ─────────────────────────────────────────────────────────────
    def logout(self):
        session.clear()
        return redirect(url_for("auth.login"))

    # ── GOOGLE OTP: SEND ──────────────────────────────────────────────────
    @staticmethod
    def google_send_otp():
        data = request.json or {}
        email = data.get('email', '').strip()
        if not email:
            return jsonify({'message': 'Email is required', 'status': 'error'}), 400

        otp_code = f"{random.randint(100000, 999999)}"
        
        # Write to local file for offline debug testing
        try:
            mock_otp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mock_otp.txt')
            with open(mock_otp_path, 'w') as f:
                f.write(otp_code)
        except Exception as e:
            print(f"Error writing mock OTP file: {e}", flush=True)
        
        otp_store[email] = {
            'code': otp_code,
            'expires_at': time.time() + 300
        }

        subject = "SportAdventure Google Sign-in Verification Code"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #0b57d0; text-align: center;">Google Sign-In Verification</h2>
                <p>Hello,</p>
                <p>You have selected <strong>{email}</strong> to sign in to SportAdventure via Google. Please use the following 6-digit verification code to complete the login:</p>
                <div style="background-color: #f1f5fb; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #0b57d0; border-radius: 5px; margin: 20px 0;">
                    {otp_code}
                </div>
                <p style="font-size: 12px; color: #777;">This code is valid for 5 minutes. If you did not request this, you can safely ignore this email.</p>
                <br>
                <p>Best regards,<br>The SportAdventure Team</p>
            </div>
        </body>
        </html>
        """
        text_content = f"Your SportAdventure Google Sign-in Verification Code is: {otp_code}. Valid for 5 minutes."

        success = send_email(email, subject, html_content, text_content)
        if success:
            return jsonify({'message': 'Verification code sent successfully', 'status': 'success'}), 200
        else:
            return jsonify({'message': 'Failed to send verification code', 'status': 'error'}), 500

    # ── GOOGLE OTP: VERIFY ────────────────────────────────────────────────
    @staticmethod
    def google_verify_otp():
        data = request.json or {}
        email = data.get('email', '').strip()
        code = data.get('code', '').strip()
        
        if not email or not code:
            return jsonify({'message': 'Email and verification code are required', 'status': 'error'}), 400

        record = otp_store.get(email)
        if not record:
            return jsonify({'message': 'No verification code was sent to this email', 'status': 'error'}), 400
            
        if time.time() > record['expires_at']:
            otp_store.pop(email, None)
            return jsonify({'message': 'Verification code has expired. Please request a new one.', 'status': 'error'}), 400

        if record['code'] != str(code).strip():
            return jsonify({'message': 'Invalid verification code', 'status': 'error'}), 400

        # Successfully verified
        otp_store.pop(email, None)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            # Auto-register Google user
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while True:
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                if not cursor.fetchone():
                    break
                username = f"{base_username}{counter}"
                counter += 1
                
            random_password = f"google_{random.randint(10000000, 99999999)}"
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                (username, email, random_password)
            )
            conn.commit()
            
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
        conn.close()

        # Log in the user in the Flask session!
        session["user"] = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "first_name": user["first_name"] or "",
            "last_name": user["last_name"] or "",
            "phone": user["phone"] or "",
            "city": user["city"] or "",
            "bio": user["bio"] or "",
            "language": user["language"] or "en",
            "role": user["role"] or "Adventure Seeker",
            "avatar": user["avatar"] or "",
            "cover": user["cover"] or "",
            "theme_preference": user["theme_preference"] or "light",
            "joined": "May 2026"
        }

        # Send welcome email
        subject = "SportAdventure Connected Successfully!"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #34a853; text-align: center;">Account Successfully Connected!</h2>
                <p>Hello {user['username']},</p>
                <p>We are excited to let you know that your Google Account (<strong>{email}</strong>) has been successfully connected to SportAdventure.</p>
                <p>You can now use this email to quickly sign in to your dashboard anytime.</p>
                <br>
                <p>Best regards,<br>The SportAdventure Team</p>
            </div>
        </body>
        </html>
        """
        text_content = f"Hello {user['username']}, your Google Account ({email}) has been successfully connected to SportAdventure!"
        send_email(email, subject, html_content, text_content)

        return jsonify({
            'message': 'Successfully connected',
            'status': 'success',
            'user': {
                'username': user['username'],
                'email': user['email']
            }
        }), 200

    # ── DASHBOARD ──────────────────────────────────────────────────────────
    def dashboard(self):
        if not self.is_logged_in():
            return redirect(url_for("auth.login"))

        user = session["user"]
        user_id = user["id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Keep session user metadata fresh
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        db_user = cursor.fetchone()
        if db_user:
            if db_user.get("status") == "suspended":
                conn.close()
                session.clear()
                flash("Your account has been suspended. Please contact support.", "danger")
                return redirect(url_for("auth.login"))

            session["user"] = {
                "id": db_user["id"],
                "username": db_user["username"],
                "email": db_user["email"],
                "first_name": db_user["first_name"] or "",
                "last_name": db_user["last_name"] or "",
                "phone": db_user["phone"] or "",
                "city": db_user["city"] or "",
                "bio": db_user["bio"] or "",
                "language": db_user["language"] or "en",
                "role": db_user["role"] or "Adventure Seeker",
                "avatar": db_user["avatar"] or "",
                "cover": db_user["cover"] or "",
                "theme_preference": db_user["theme_preference"] or "light",
                "joined": "May 2026"
            }
            user = session["user"]

        # 1. Auto-complete any confirmed bookings whose date has already passed.
        from datetime import datetime
        today_str = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(
            "UPDATE bookings SET status = 'completed' "
            "WHERE user_id = ? AND status = 'confirmed' AND date < ?",
            (user_id, today_str)
        )
        conn.commit()

        # Fetch bookings
        cursor.execute("SELECT * FROM bookings WHERE user_id = ? ORDER BY id DESC", (user_id,))
        bookings_data = cursor.fetchall()
        
        # Fetch wishlist count for badge
        cursor.execute("SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?", (user_id,))
        w_row = cursor.fetchone()
        wishlist_count = w_row["count"] if w_row else 0

        # Calculate dynamic activity availability metrics based on all active bookings
        CAPACITIES = {
            "Paragliding": 10,
            "Bungee Jumping": 15,
            "White Water Rafting": 20,
            "Trekking": 15,
            "Canyoning": 10,
            "Zip-lining": 20
        }
        
        cursor.execute("SELECT activity, date, SUM(people) as booked_count FROM bookings WHERE status != 'cancelled' GROUP BY activity, date")
        avail_rows = cursor.fetchall()
        availability = {}
        for row in avail_rows:
            act_name = row["activity"]
            date_str = row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"])
            booked = int(row["booked_count"])
            capacity = CAPACITIES.get(act_name, 15)
            remaining = max(0, capacity - booked)
            fill_pct = min(100, int((booked / capacity) * 100))
            
            if remaining == 0:
                status = "soldout"
            elif remaining <= 3:
                status = "limited"
            else:
                status = "available"
                
            if date_str not in availability:
                availability[date_str] = {}
            availability[date_str][act_name] = {
                "status": status,
                "remaining": remaining,
                "capacity": capacity,
                "fill_pct": fill_pct
            }
        
        # Fetch notifications
        cursor.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 15", (user_id,)
        )
        notifications = cursor.fetchall()

        conn.close()

        # Enrich bookings with display metadata
        bookings_list = []
        for b in bookings_data:
            b_dict = dict(b)
            act_name = b_dict.get("activity", "").strip().lower()

            internal_notes = b_dict.get("internal_notes") or ""
            is_event = internal_notes.startswith("event_")
            event_details = None
            if is_event:
                try:
                    event_id = int(internal_notes.split("_")[1])
                    from app.models.database import get_event_by_id
                    event_details = get_event_by_id(event_id)
                except Exception:
                    pass

            if event_details:
                b_dict["img"] = event_details["image_url"] or "Mountain-Main.png"
                b_dict["location"] = event_details["location"]
                b_dict["duration"] = event_details["duration"] or "3 hours"
            else:
                act_key = None
                for key, val in ACTIVITIES.items():
                    if val["name"].lower() == act_name or key == act_name:
                        act_key = key
                        break

                if act_key:
                    act = ACTIVITIES[act_key]
                    b_dict["img"] = act["img"]
                    b_dict["location"] = act["location"]
                    b_dict["duration"] = act["duration"]
                else:
                    b_dict["img"] = "Mountain-Main.png"
                    b_dict["location"] = "Nepal"
                    b_dict["duration"] = "1 day"

            bookings_list.append(b_dict)

        # Calculate live metrics
        stats = {
            "total": len(bookings_list),
            "upcoming": sum(1 for b in bookings_list if b["status"] == "confirmed"),
            "completed": sum(1 for b in bookings_list if b["status"] == "completed"),
            "spent": sum(float(b.get("total", 0)) for b in bookings_list),
        }

        return render_template(
            "Dashboard.html",
            user=user,
            stats=stats,
            bookings=bookings_list,
            activities=ACTIVITIES,
            wishlist_count=wishlist_count,
            availability=availability,
            notifications=notifications
        )

    # ── CANCEL BOOKING ─────────────────────────────────────────────────────
    def cancel_booking(self):
        if not self.is_logged_in():
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        booking_id = request.form.get("booking_id")
        if not booking_id:
            return jsonify({"success": False, "error": "Missing booking ID"}), 400

        user_id = self.get_current_user_id()

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Verify the booking belongs to this user and is currently confirmed
            cursor.execute("SELECT * FROM bookings WHERE id = ? AND user_id = ?", (booking_id, user_id))
            booking = cursor.fetchone()
            if not booking:
                conn.close()
                return jsonify({"success": False, "error": "Booking not found"}), 404

            if booking["status"] != "confirmed":
                conn.close()
                return jsonify({"success": False, "error": "Only confirmed bookings can be cancelled"}), 400

            # Update status to cancelled
            cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
            conn.commit()

            # Notify user of cancellation
            try:
                from app.controlers.Auth_Admin import send_notification, log_audit
                send_notification(
                    user_id,
                    f"Booking #{booking_id} Cancelled",
                    f"Your booking for '{booking['activity']}' on {booking['date']} has been successfully cancelled."
                )

                # Audit log — record user self-cancellation
                log_audit(
                    user_id,
                    "User Self-Cancel Booking",
                    f"Booking #{booking_id}",
                    f"User cancelled own booking for '{booking['activity']}' on {booking['date']}"
                )
            except Exception as notif_err:
                print("Notification/Audit failure during booking cancel:", notif_err)

            conn.close()
            return jsonify({"success": True}), 200
        except Exception as e:
            print("Error cancelling booking:", e)
            conn.close()
            return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500

    # ── BOOK ACTIVITY ──────────────────────────────────────────────────────
    def book_activity(self):
        if not self.is_logged_in():
            return redirect(url_for("auth.login"))

        if request.method == "POST":
            activity_id = request.form.get("activity_id", "").strip().lower()

            date = request.form.get("date", "")

            try:
                people = int(request.form.get("people", 1))
            except ValueError:
                people = 1

            act = ACTIVITIES.get(activity_id)
            if not act:
                for key, val in ACTIVITIES.items():
                    if val["name"].lower() == activity_id:
                        act = val
                        break

            if not act:
                act = ACTIVITIES["paragliding"]

            price = float(act["price"])
            total = price * people
            activity_name = act["name"]

            user_id = self.get_current_user_id()

            payment_method = request.form.get("payment_method", "qr").strip()
            txn_code = request.form.get("txn_code", "").strip()
            booking_status = "confirmed"

            if date:
                conn = get_db_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO bookings (user_id, activity, date, people, price, total, status, payment_status, payment_method, txn_code) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (user_id, activity_name, date, people, price, total, booking_status, "confirmed", payment_method, txn_code)
                    )
                    cursor.execute(
                        "INSERT INTO notifications (user_id, title, message, status) VALUES (?, ?, ?, 'unread')",
                        (
                            user_id,
                            "Booking Confirmed",
                            f"Your booking for {activity_name} on {date} has been confirmed successfully!"
                        )
                    )
                    conn.commit()
                    flash(f"🎉 {activity_name} booked successfully!")
                except Exception as e:
                    print("Error saving booking:", e)
                    flash("An error occurred. Please try again.")
                conn.close()

        return redirect(url_for("auth.dashboard"))


    # ── PROFILE MANAGEMENT ─────────────────────────────────────────────────
    def manage(self):
        if not self.is_logged_in():
            return redirect(url_for("auth.login"))

        user_id = self.get_current_user_id()

        if request.method == "POST":
            # Extract parameters supporting both JSON/form formats
            if request.is_json:
                data = request.json or {}
                first_name = data.get("firstName", "").strip()
                last_name = data.get("lastName", "").strip()
                email = data.get("email", "").strip()
                phone = data.get("phone", "").strip()
                city = data.get("city", "").strip()
                bio = data.get("bio", "").strip()
                language = data.get("language", "en").strip()
                role = data.get("role", "Adventure Seeker").strip()
                avatar = data.get("avatar", "")
                cover = data.get("cover", "")
                theme_pref = data.get("theme_preference", "light").strip()
            else:
                first_name = request.form.get("firstName", "").strip()
                last_name = request.form.get("lastName", "").strip()
                email = request.form.get("email", "").strip()
                phone = request.form.get("phone", "").strip()
                city = request.form.get("city", "").strip()
                bio = request.form.get("bio", "").strip()
                language = request.form.get("language", "en").strip()
                role = request.form.get("role", "Adventure Seeker").strip()
                avatar = request.form.get("avatar", "")
                cover = request.form.get("cover", "")
                theme_pref = request.form.get("theme_preference", "light").strip()

            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                # Update user columns
                cursor.execute("""
                    UPDATE users 
                    SET first_name = ?, last_name = ?, email = ?, phone = ?, city = ?,
                        bio = ?, language = ?, role = ?, avatar = ?, cover = ?, theme_preference = ? 
                    WHERE id = ?
                """, (first_name, last_name, email, phone, city, bio, language, role, avatar, cover, theme_pref, user_id))
                conn.commit()
                
                # Fetch fresh updated record
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                db_user = cursor.fetchone()
                
                # Update session keys
                session["user"] = {
                    "id": db_user["id"],
                    "username": db_user["username"],
                    "email": db_user["email"],
                    "first_name": db_user["first_name"] or "",
                    "last_name": db_user["last_name"] or "",
                    "phone": db_user["phone"] or "",
                    "city": db_user["city"] or "",
                    "bio": db_user["bio"] or "",
                    "language": db_user["language"] or "en",
                    "role": db_user["role"] or "Adventure Seeker",
                    "avatar": db_user["avatar"] or "",
                    "cover": db_user["cover"] or "",
                    "theme_preference": db_user["theme_preference"] or "light",
                    "joined": "May 2026"
                }
                
                if request.is_json:
                    return jsonify({"message": "Profile updated successfully!", "status": "success", "user": session["user"]}), 200
                flash("Profile updated successfully!", "success")
            except Exception as e:
                print("Error updating profile in SQLite:", e)
                if request.is_json:
                    return jsonify({"message": f"Profile update failed: {str(e)}", "status": "error"}), 500
                flash("Failed to update profile.", "danger")
            finally:
                conn.close()

        # Render GET page with synced DB record
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        db_user = cursor.fetchone()
        
        # Fetch wishlist count for badge
        cursor.execute("SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?", (user_id,))
        w_row = cursor.fetchone()
        wishlist_count = w_row["count"] if w_row else 0
        conn.close()

        return render_template("manage_profile.html", user=db_user or session["user"], wishlist_count=wishlist_count)

    # ── WISHLIST PAGE ──────────────────────────────────────────────────────
    def wishlist_page(self):
        if not self.is_logged_in():
            return redirect(url_for("auth.login"))

        user = session["user"]
        user_id = user["id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT activity_id FROM wishlist WHERE user_id = ?", (user_id,))
        wish_rows = cursor.fetchall()
        
        # Fresh wishlist count
        wishlist_count = len(wish_rows)
        conn.close()

        wishlist_items = []
        for row in wish_rows:
            act_id = row["activity_id"]
            if act_id in ACTIVITIES:
                act = ACTIVITIES[act_id]
                wishlist_items.append({
                    "id": act_id,
                    "name": act["name"],
                    "price": act["price"],
                    "location": act["location"],
                    "duration": act["duration"],
                    "img": act["img"],
                    "tickets_left": random.randint(2, 12)  # High-fidelity mock dynamic indicator
                })
            elif act_id and act_id.startswith("event_"):
                try:
                    event_id = int(act_id.split("_")[1])
                    from app.models.database import get_event_by_id
                    event = get_event_by_id(event_id)
                    if event:
                        wishlist_items.append({
                            "id": act_id,
                            "name": event["title"],
                            "price": event["price"],
                            "location": event["location"],
                            "duration": event["duration"] or "3 hours",
                            "img": event["image_url"] or "Mountain-Main.png",
                            "tickets_left": event["tickets_left"]
                        })
                except Exception as ex:
                    print("Error loading wishlisted event:", ex)

        return render_template("wishlist.html", user=user, wishlist=wishlist_items, wishlist_count=wishlist_count)

    # ── TOGGLE WISHLIST API ────────────────────────────────────────────────
    def toggle_wishlist(self):
        if not self.is_logged_in():
            return jsonify({"message": "Unauthorized", "status": "error"}), 401

        data = request.json or {}
        activity_id = data.get("activity_id", "").strip().lower()
        is_event = activity_id and activity_id.startswith("event_")
        if not activity_id or (activity_id not in ACTIVITIES and not is_event):
            return jsonify({"message": "Invalid activity ID", "status": "error"}), 400

        user_id = self.get_current_user_id()

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if already saved
        cursor.execute("SELECT * FROM wishlist WHERE user_id = ? AND activity_id = ?", (user_id, activity_id))
        existing = cursor.fetchone()
        
        saved = False
        try:
            if existing:
                cursor.execute("DELETE FROM wishlist WHERE user_id = ? AND activity_id = ?", (user_id, activity_id))
                saved = False
            else:
                cursor.execute("INSERT INTO wishlist (user_id, activity_id) VALUES (?, ?)", (user_id, activity_id))
                saved = True
            conn.commit()
        except Exception as e:
            print("Error toggling wishlist item:", e)
            conn.close()
            return jsonify({"message": "Database action failed", "status": "error"}), 500

        conn.close()
        return jsonify({"status": "success", "saved": saved}), 200

    # ── SECURE FORGOT & RESET PASSWORD ─────────────────────────────────────
    def forgot_password(self):
        if request.method == "POST":
            data = request.json or {}
            action = data.get("action", "").strip()
            email = data.get("email", "").strip()

            if action == "send_otp":
                if not email:
                    return jsonify({"message": "Email is required.", "status": "error"}), 400

                # Verify email exists in database
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                user_data = cursor.fetchone()
                conn.close()

                if not user_data:
                    return jsonify({"message": "This email is not registered.", "status": "error"}), 404

                # Generate code and save
                otp_code = f"{random.randint(100000, 999999)}"
                
                try:
                    mock_otp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mock_otp.txt')
                    with open(mock_otp_path, 'w') as f:
                        f.write(otp_code)
                except Exception as e:
                    print(f"Error writing mock OTP: {e}")

                otp_store[email] = {
                    "code": otp_code,
                    "expires_at": time.time() + 300
                }

                # Send email
                subject = "SportAdventure Password Reset Request"
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #ff4f4f; text-align: center;">Password Reset Verification</h2>
                        <p>Hello,</p>
                        <p>We received a request to reset your password. Use the following 6-digit verification code to proceed:</p>
                        <div style="background-color: #fdf2f2; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #ff4f4f; border-radius: 5px; margin: 20px 0;">
                            {otp_code}
                        </div>
                        <p style="font-size: 12px; color: #777;">This code is valid for 5 minutes. If you did not request this, you can safely ignore this email.</p>
                        <br>
                        <p>Best regards,<br>The SportAdventure Team</p>
                    </div>
                </body>
                </html>
                """
                text_content = f"Your SportAdventure Password Reset Verification Code is: {otp_code}. Valid for 5 minutes."

                success = send_email(email, subject, html_content, text_content)
                if success:
                    return jsonify({"message": "Verification code sent to your email!", "status": "success"}), 200
                else:
                    return jsonify({"message": "SMTP mailing failure.", "status": "error"}), 500

            elif action == "reset":
                code = data.get("code", "").strip()
                new_password = data.get("password", "")

                if not email or not code or not new_password:
                    return jsonify({"message": "All fields are required.", "status": "error"}), 400

                # Validate OTP
                record = otp_store.get(email)
                if not record:
                    return jsonify({"message": "No code was sent to this email.", "status": "error"}), 400

                if time.time() > record["expires_at"]:
                    otp_store.pop(email, None)
                    return jsonify({"message": "Verification code expired. Request a new one.", "status": "error"}), 400

                if record["code"] != code:
                    return jsonify({"message": "Invalid verification code.", "status": "error"}), 400

                # Clear OTP record
                otp_store.pop(email, None)

                # Update user password in SQLite
                conn = get_db_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
                    conn.commit()
                except Exception as e:
                    print("Error updating password in SQLite:", e)
                    conn.close()
                    return jsonify({"message": "Database update failed.", "status": "error"}), 500

                conn.close()
                return jsonify({"message": "Password reset successful! Please log in.", "status": "success"}), 200

        # Renders the reset.html forgot/reset view on GET
        return render_template("reset.html")

    # ── GALLERY PAGE ──────────────────────────────────────────────────────
    def gallery(self):
        user = session.get("user")
        wishlist_count = 0
        if user:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?", (user["id"],))
            row = cursor.fetchone()
            wishlist_count = row["count"] if row else 0
            conn.close()

        conn = get_db_connection()
        cursor = conn.cursor()
        posts = cursor.execute(
            "SELECT p.*, u.username FROM posts p LEFT JOIN users u ON p.admin_id = u.id ORDER BY p.created_at DESC"
        ).fetchall()
        conn.close()

        posts_list = [dict(p) for p in posts]
        return render_template("gallery.html", user=user, posts=posts_list, wishlist_count=wishlist_count)

    # ── GALLERY ADD POST (Admin only) ─────────────────────────────────────
    def gallery_add(self):
        user = session.get("user")
        if not user:
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        # Check admin role
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM users WHERE id = ?", (user["id"],))
        db_user = cursor.fetchone()
        if not db_user or db_user["status"] != "active" or user.get("role") not in ("super_admin", "admin"):
            conn.close()
            return jsonify({"success": False, "message": "Admin access required"}), 403

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        image_file = request.files.get("image")

        if not image_file or not image_file.filename:
            conn.close()
            return jsonify({"success": False, "message": "Image is required"}), 400

        # Save image to static/images/gallery/
        import uuid
        gallery_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "images", "gallery")
        os.makedirs(gallery_dir, exist_ok=True)
        ext = os.path.splitext(image_file.filename)[1].lower()
        filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(gallery_dir, filename)
        image_file.save(save_path)
        image_url = f"gallery/{filename}"

        cursor.execute(
            "INSERT INTO posts (admin_id, title, image_url, description) VALUES (?, ?, ?, ?)",
            (user["id"], title, image_url, description)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Post created successfully!"})

    # ── GALLERY DELETE POST (Admin only) ──────────────────────────────────
    def gallery_delete(self, post_id):
        user = session.get("user")
        if not user or user.get("role") not in ("super_admin", "admin"):
            return jsonify({"success": False, "message": "Admin access required"}), 403

        conn = get_db_connection()
        cursor = conn.cursor()
        post = cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not post:
            conn.close()
            return jsonify({"success": False, "message": "Post not found"}), 404

        # Delete image file
        try:
            img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "images", post["image_url"])
            if os.path.exists(img_path):
                os.remove(img_path)
        except Exception:
            pass

        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})

    # ── REVIEWS PAGE ──────────────────────────────────────────────────────
    def reviews(self):
        user = session.get("user")
        wishlist_count = 0
        if user:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?", (user["id"],))
            row = cursor.fetchone()
            wishlist_count = row["count"] if row else 0
            conn.close()

        conn = get_db_connection()
        cursor = conn.cursor()
        reviews_data = cursor.execute(
            "SELECT r.*, u.username FROM reviews r LEFT JOIN users u ON r.user_id = u.id ORDER BY r.created_at DESC"
        ).fetchall()
        conn.close()

        reviews_list = [dict(r) for r in reviews_data]
        return render_template("review.html", user=user, reviews=reviews_list, wishlist_count=wishlist_count)

    # ── ADD REVIEW ────────────────────────────────────────────────────────
    def add_review(self):
        if not self.is_logged_in():
            flash("Please log in to leave a review.", "danger")
            return redirect(url_for("auth.login"))

        user = session["user"]
        activity = request.form.get("activity", "").strip()
        rating = request.form.get("rating", 5)
        review_text = request.form.get("review", "").strip()

        if not activity or not review_text:
            flash("Activity and review text are required.", "danger")
            return redirect(url_for("auth.reviews"))

        try:
            rating = int(rating)
            rating = max(1, min(5, rating))
        except (ValueError, TypeError):
            rating = 5

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reviews (user_id, activity, rating, review) VALUES (?, ?, ?, ?)",
            (user["id"], activity, rating, review_text)
        )
        conn.commit()
        conn.close()
        flash("Your review has been submitted!", "success")
        return redirect(url_for("auth.reviews"))

    # ── EDIT REVIEW ───────────────────────────────────────────────────────
    def edit_review(self, review_id):
        if not self.is_logged_in():
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        user = session["user"]
        data = request.json or {}
        review_text = data.get("review", "").strip()
        rating = data.get("rating", None)

        conn = get_db_connection()
        cursor = conn.cursor()
        existing = cursor.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()

        if not existing:
            conn.close()
            return jsonify({"success": False, "message": "Review not found"}), 404

        # Allow edit only if user owns the review OR is admin
        is_admin = user.get("role") in ("super_admin", "admin")
        if existing["user_id"] != user["id"] and not is_admin:
            conn.close()
            return jsonify({"success": False, "message": "Permission denied"}), 403

        new_rating = existing["rating"]
        if rating is not None:
            try:
                new_rating = max(1, min(5, int(rating)))
            except (ValueError, TypeError):
                pass

        new_text = review_text if review_text else existing["review"]
        cursor.execute(
            "UPDATE reviews SET review = ?, rating = ? WHERE id = ?",
            (new_text, new_rating, review_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Review updated!"})

    # ── DELETE REVIEW ─────────────────────────────────────────────────────
    def delete_review(self, review_id):
        if not self.is_logged_in():
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        user = session["user"]
        conn = get_db_connection()
        cursor = conn.cursor()
        existing = cursor.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()

        if not existing:
            conn.close()
            return jsonify({"success": False, "message": "Review not found"}), 404

        is_admin = user.get("role") in ("super_admin", "admin")
        if existing["user_id"] != user["id"] and not is_admin:
            conn.close()
            return jsonify({"success": False, "message": "Permission denied"}), 403

        cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})

    # ── MARK NOTIFICATION READ ─────────────────────────────────────────────
    def mark_notification_read(self):
        if not self.is_logged_in():
            return jsonify({"success": False, "error": "Not logged in"}), 401

        notif_id = request.form.get("id") or (request.json.get("id") if request.json else None)
        if not notif_id:
            return jsonify({"success": False, "error": "Missing notification ID"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE notifications SET status = 'read' WHERE id = ? AND user_id = ?",
                (notif_id, session["user"]["id"])
            )
            conn.commit()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            conn.close()
            print("Error marking notification as read:", e)
            return jsonify({"success": False, "error": "Database error"}), 500

    # ── GET ALL NOTIFICATIONS API ──────────────────────────────────────────
    def api_get_notifications(self):
        if not self.is_logged_in():
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        
        user_id = self.get_current_user_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 15", (user_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            notifications = []
            for r in rows:
                notif = dict(r)
                if hasattr(notif["created_at"], "strftime"):
                    notif["created_at"] = notif["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    notif["created_at"] = str(notif["created_at"])
                notifications.append(notif)
                
            return jsonify(notifications)
        except Exception as e:
            conn.close()
            print("Error fetching notifications API:", e)
            return jsonify({"success": False, "error": "Database error"}), 500

    # ── MARK ALL NOTIFICATIONS AS READ API ─────────────────────────────────
    def mark_all_notifications_read(self):
        if not self.is_logged_in():
            return jsonify({"success": False, "error": "Not logged in"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE notifications SET status = 'read' WHERE user_id = ?",
                (session["user"]["id"],)
            )
            conn.commit()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            conn.close()
            print("Error marking all notifications as read:", e)
            return jsonify({"success": False, "error": "Database error"}), 500