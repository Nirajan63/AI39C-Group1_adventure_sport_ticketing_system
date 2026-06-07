import json
from functools import wraps
from flask import render_template, request, session, redirect, url_for, flash, jsonify
from datetime import datetime
from App.Controllers.baseController import BaseController
from App.Models.user import User
from App.Models.data import Database


# ── Helper to log audit actions ──────────────────────────────────────────
def log_audit(admin_id, action, target, details=""):
    db = Database()
    try:
        db.execute(
            "INSERT INTO audit_logs (admin_id, action, target_record, details) VALUES (%s, %s, %s, %s)",
            (admin_id, action, target, details)
        )
    except Exception as e:
        print("[AUDIT ERROR]:", e)
    finally:
        db.close()


# ── Helper to send in-app notifications ──────────────────────────────────
def send_notification(user_id, title, message):
    db = Database()
    try:
        db.execute(
            "INSERT INTO notifications (user_id, title, message, status) VALUES (%s, %s, %s, 'unread')",
            (user_id, title, message)
        )
    except Exception as e:
        print("[NOTIFICATION ERROR]:", e)
    finally:
        db.close()


# ── Decorator to enforce admin/staff role ───────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth_admin.login_admin"))
        # Re-validate role AND status from DB on every protected request
        # This ensures role demotions and suspensions take effect immediately.
        db = Database()
        db_user = db.fetch_one(
            "SELECT role, status FROM users WHERE id = %s",
            (session["user"]["id"],)
        )
        db.close()
        if not db_user:
            session.clear()
            flash("Account not found. Please log in again.", "danger")
            return redirect(url_for("auth_admin.login_admin"))
        if db_user.get("status") == "suspended":
            session.clear()
            flash("Your account has been suspended. Please contact support.", "danger")
            return redirect(url_for("auth.login"))
        live_role = db_user.get("role")
        if live_role not in ["admin", "super_admin", "staff"]:
            session.clear()
            flash("Access denied: Administrative permissions required.", "danger")
            return redirect(url_for("auth.login"))
        # Keep session role in sync with DB
        session["user"]["role"] = live_role
        return f(*args, **kwargs)
    return decorated_function


class AuthController_Admin(BaseController):

    def __init__(self):
        self.user_model = User()

    # ── ADMIN LOGIN ────────────────────────────────────────────────────────
    def login_admin(self):
        if self.is_logged_in():
            role = session["user"].get("role")
            if role in ["admin", "super_admin", "staff"]:
                return redirect(url_for("auth_admin.dashboard_admin"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                flash("Username/email and password are required.", "danger")
                return render_template("login_Admin.html")

            # Check users
            user_data = self.user_model.find_by("email", username)
            if not user_data:
                user_data = self.user_model.find_by("name", username)

            if user_data:
                user = User.from_db(user_data)
                if user.check_password(password):
                    # Check role
                    if user_data["role"] not in ["admin", "super_admin", "staff"]:
                        flash("Access denied: Account is not an administrator.", "danger")
                        return render_template("login_Admin.html")
                    # Check status
                    if user_data.get("status") == "suspended":
                        flash("Account suspended.", "danger")
                        return render_template("login_Admin.html")

                    session["user"] = {
                        "id":       user_data["id"],
                        "name":     user_data["name"],
                        "username": user_data["name"],
                        "email":    user_data["email"],
                        "role":     user_data["role"],
                        "joined":   "May 2026",
                    }
                    log_audit(user_data["id"], "Login", f"User #{user_data['id']}", "Successful admin login")

                    # Force password change if flagged (e.g. first-time seeded admin)
                    if user_data.get("must_change_password") == 1:
                        session["force_pw_change"] = True
                        flash("⚠️ You must change your default password before continuing.", "warning")
                        return redirect(url_for("auth_admin.change_password_admin"))

                    return redirect(url_for("auth_admin.dashboard_admin"))

            flash("Invalid credentials.", "danger")

        return render_template("login_Admin.html")

    # ── ADMIN LOGOUT ───────────────────────────────────────────────────────
    def logout_admin(self):
        if "user" in session:
            admin_id = session["user"]["id"]
            log_audit(admin_id, "Logout", f"User #{admin_id}", "Admin logged out")
        session.clear()
        return redirect(url_for("auth_admin.login_admin"))

    # ── CHANGE PASSWORD (forced on first login) ────────────────────────────
    def change_password_admin(self):
        """Forces the seeded admin to set a new password before accessing the dashboard."""
        if "user" not in session:
            return redirect(url_for("auth_admin.login_admin"))

        if request.method == "POST":
            new_pw = request.form.get("new_password", "").strip()
            confirm_pw = request.form.get("confirm_password", "").strip()

            if not new_pw or not confirm_pw:
                flash("Both fields are required.", "danger")
                return render_template("change_password_Admin.html")

            if len(new_pw) < 8:
                flash("Password must be at least 8 characters.", "danger")
                return render_template("change_password_Admin.html")

            if new_pw == "admin123":
                flash("You cannot reuse the default system password. Choose a new unique password.", "warning")
                return render_template("change_password_Admin.html")

            if new_pw != confirm_pw:
                flash("Passwords do not match.", "danger")
                return render_template("change_password_Admin.html")

            from werkzeug.security import generate_password_hash
            user_id = session["user"]["id"]
            db = Database()
            db.execute(
                "UPDATE users SET password = %s, must_change_password = 0 WHERE id = %s",
                (generate_password_hash(new_pw), user_id)
            )
            db.close()

            # Clear forced change flag
            session.pop("force_pw_change", None)
            log_audit(user_id, "Password Changed", f"User #{user_id}", "Admin changed default password")
            flash("✅ Password updated successfully. Welcome to the admin portal.", "success")
            return redirect(url_for("auth_admin.dashboard_admin"))

        return render_template("change_password_Admin.html")

    # ── ADMIN DASHBOARD VIEW ───────────────────────────────────────────────
    @admin_required
    def dashboard_admin(self):
        db = Database()
        
        # Gather overview counts
        total_users = db.fetch_one("SELECT COUNT(*) AS total FROM users")["total"]
        total_activities = db.fetch_one("SELECT COUNT(*) AS total FROM activities")["total"]
        total_bookings = db.fetch_one("SELECT COUNT(*) AS total FROM bookings")["total"]
        active_bookings = db.fetch_one("SELECT COUNT(*) AS total FROM bookings WHERE status = 'confirmed'")["total"]
        completed_activities = db.fetch_one("SELECT COUNT(*) AS total FROM bookings WHERE status = 'completed'")["total"]
        cancelled_bookings = db.fetch_one("SELECT COUNT(*) AS total FROM bookings WHERE status = 'cancelled'")["total"]
        
        # Payment indicators
        total_revenue = db.fetch_one("SELECT SUM(total) AS total FROM bookings WHERE payment_status = 'confirmed' AND status != 'cancelled'")["total"] or 0
        monthly_revenue = db.fetch_one(
            "SELECT SUM(total) AS total FROM bookings WHERE payment_status = 'confirmed' AND status != 'cancelled' AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')"
        )["total"] or 0
        pending_payments = db.fetch_one("SELECT COUNT(*) AS total FROM bookings WHERE payment_status = 'pending'")["total"]

        stats = {
            "total_users": total_users,
            "total_activities": total_activities,
            "total_bookings": total_bookings,
            "active_bookings": active_bookings,
            "completed_activities": completed_activities,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "pending_payments": pending_payments
        }

        # Fetch activities for calendar mapping
        activities_data = db.fetch_all("SELECT * FROM activities")
        activities_dict = {}
        for a in activities_data:
            activities_dict[a['id']] = dict(a)

        db.close()

        return render_template(
            "dashboard_Admin.html",
            user=session["user"],
            stats=stats,
            activities=activities_dict
        )

    # ── ACTIVITY CRUD ENDPOINTS ────────────────────────────────────────────
    @admin_required
    def api_activities(self):
        db = Database()
        if request.method == "GET":
            activities = db.fetch_all("SELECT * FROM activities")
            db.close()
            return jsonify(activities)

        elif request.method == "POST":
            # Guard permission
            if session["user"].get("role") == "staff":
                db.close()
                return jsonify({"success": False, "message": "Permission denied"}), 403

            data = request.json
            act_id = data.get("id", "").strip().lower()
            name = data.get("name", "").strip()
            price = float(data.get("price", 0))
            capacity = int(data.get("capacity", 20))
            duration = data.get("duration", "1 hour").strip()
            location = data.get("location", "").strip()
            difficulty = data.get("difficulty", "Medium").strip()
            category = data.get("category", "Adventure").strip()
            description = data.get("description", "").strip()
            img = data.get("img", "Mountain-Main.png").strip()
            pic = data.get("pic", "Trekking_Pic.jpeg").strip()
            available_dates = data.get("available_dates", "").strip()

            if not act_id or not name:
                db.close()
                return jsonify({"success": False, "message": "ID and Name are required"}), 400

            # Check if exists
            exists = db.fetch_one("SELECT * FROM activities WHERE id = %s", (act_id,))
            if exists:
                db.close()
                return jsonify({"success": False, "message": "Activity ID already exists"}), 400

            db.execute(
                "INSERT INTO activities (id, name, description, category, price, duration, capacity, img, pic, location, difficulty, status, available_dates) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active', %s)",
                (act_id, name, description, category, price, duration, capacity, img, pic, location, difficulty, available_dates)
            )
            log_audit(session["user"]["id"], "Create Activity", act_id, f"Created activity: {name}")
            db.close()
            return jsonify({"success": True, "message": "Activity created successfully"})

    @admin_required
    def api_activity_detail(self, activity_id):
        # Guard permission
        if session["user"].get("role") == "staff":
            return jsonify({"success": False, "message": "Permission denied"}), 403

        db = Database()
        if request.method == "PUT":
            data = request.json
            name = data.get("name", "").strip()
            price = float(data.get("price", 0))
            capacity = int(data.get("capacity", 20))
            duration = data.get("duration", "1 hour").strip()
            location = data.get("location", "").strip()
            difficulty = data.get("difficulty", "Medium").strip()
            category = data.get("category", "Adventure").strip()
            description = data.get("description", "").strip()
            status = data.get("status", "active").strip()
            img = data.get("img", "Mountain-Main.png").strip()
            pic = data.get("pic", "Trekking_Pic.jpeg").strip()
            available_dates = data.get("available_dates", "").strip()

            if not name:
                db.close()
                return jsonify({"success": False, "message": "Name is required"}), 400

            db.execute(
                "UPDATE activities SET name=%s, description=%s, category=%s, price=%s, duration=%s, capacity=%s, img=%s, pic=%s, location=%s, difficulty=%s, status=%s, available_dates=%s WHERE id=%s",
                (name, description, category, price, duration, capacity, img, pic, location, difficulty, status, available_dates, activity_id)
            )
            log_audit(session["user"]["id"], "Update Activity", activity_id, f"Updated activity: {name} (Status: {status})")

            # Notify affected users whose upcoming bookings reference this activity
            try:
                affected = db.fetch_all(
                    "SELECT DISTINCT user_id FROM bookings WHERE activity = %s AND status = 'confirmed'",
                    (name,)
                )
                notify_msg = (
                    f"The activity '{name}' has been updated by our team. "
                    f"Please review your booking details to confirm availability."
                )
                for row in affected:
                    send_notification(row["user_id"], f"Activity Updated: {name}", notify_msg)
            except Exception as notif_err:
                import logging
                logging.getLogger(__name__).warning("Activity edit notification failed: %s", notif_err)

            db.close()
            return jsonify({"success": True, "message": "Activity updated successfully"})

        elif request.method == "DELETE":
            # Archive instead of physical delete
            db.execute("UPDATE activities SET status = 'archived' WHERE id = %s", (activity_id,))
            log_audit(session["user"]["id"], "Archive Activity", activity_id, f"Archived activity ID: {activity_id}")
            db.close()
            return jsonify({"success": True, "message": "Activity archived successfully"})

    @admin_required
    def api_duplicate_activity(self):
        if session["user"].get("role") == "staff":
            return jsonify({"success": False, "message": "Permission denied"}), 403

        data = request.json
        source_id = data.get("source_id", "").strip()
        new_id = data.get("new_id", "").strip().lower()
        new_name = data.get("new_name", "").strip()

        if not source_id or not new_id or not new_name:
            return jsonify({"success": False, "message": "All duplicate parameters are required"}), 400

        db = Database()
        source = db.fetch_one("SELECT * FROM activities WHERE id = %s", (source_id,))
        if not source:
            db.close()
            return jsonify({"success": False, "message": "Source activity not found"}), 404

        exists = db.fetch_one("SELECT * FROM activities WHERE id = %s", (new_id,))
        if exists:
            db.close()
            return jsonify({"success": False, "message": "Duplicate ID already exists"}), 400

        db.execute(
            "INSERT INTO activities (id, name, description, category, price, duration, capacity, img, pic, location, difficulty, status, available_dates) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active', %s)",
            (new_id, new_name, source["description"], source["category"], source["price"], source["duration"],
             source["capacity"], source["img"], source["pic"], source["location"], source["difficulty"], source["available_dates"])
        )
        log_audit(session["user"]["id"], "Duplicate Activity", new_id, f"Duplicated activity from {source_id} to {new_id}")
        db.close()
        return jsonify({"success": True, "message": "Activity duplicated successfully"})

    # ── BOOKING MANAGEMENT ENDPOINTS ───────────────────────────────────────
    @admin_required
    def api_bookings(self):
        db = Database()
        query = """
            SELECT b.*, u.name AS user_name, u.email AS user_email
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            ORDER BY b.id DESC
        """
        bookings = db.fetch_all(query)
        db.close()
        return jsonify(bookings)

    @admin_required
    def api_booking_detail(self, booking_id):
        db = Database()
        booking = db.fetch_one("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        if not booking:
            db.close()
            return jsonify({"success": False, "message": "Booking not found"}), 404

        if request.method == "PUT":
            data = request.json
            status = data.get("status", booking["status"])
            payment_status = data.get("payment_status", booking["payment_status"])
            internal_notes = data.get("internal_notes", booking["internal_notes"])
            date = data.get("date", booking["date"])
            people = int(data.get("people", booking["people"]))
            price = float(data.get("price", booking["price"]))
            total = price * people

            # Guard refund action to admin/super_admin
            if payment_status == "refunded" and session["user"].get("role") == "staff":
                db.close()
                return jsonify({"success": False, "message": "Permission denied for refund operations"}), 403

            db.execute(
                "UPDATE bookings SET status=%s, payment_status=%s, internal_notes=%s, date=%s, people=%s, price=%s, total=%s WHERE id=%s",
                (status, payment_status, internal_notes, date, people, price, total, booking_id)
            )

            # Send Notification
            note_title = f"Booking #{booking_id} Updated"
            note_msg = f"Your booking for {booking['activity']} on {date} has been updated to: Status: {status}, Payment: {payment_status}."
            send_notification(booking["user_id"], note_title, note_msg)

            log_audit(
                session["user"]["id"], 
                "Modify Booking", 
                f"Booking #{booking_id}", 
                f"Status: {status}, Payment: {payment_status}, Date: {date}"
            )
            db.close()
            return jsonify({"success": True, "message": "Booking updated successfully"})

    # ── PAYMENT MANAGEMENT ENDPOINTS ───────────────────────────────────────
    @admin_required
    def api_payments(self):
        db = Database()
        # Include ALL bookings that have a payment record — status confirmed OR pending OR refunded
        query = """
            SELECT b.id AS booking_id, b.activity, b.date, b.total, b.payment_status,
                   b.payment_method, b.txn_code, b.status,
                   u.name AS user_name, u.email AS user_email
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            ORDER BY b.id DESC
        """
        payments = db.fetch_all(query)
        db.close()
        return jsonify(payments)

    @admin_required
    def api_verify_payment(self):
        data = request.json
        booking_id = data.get("booking_id")
        if not booking_id:
            return jsonify({"success": False, "message": "Booking ID required"}), 400

        db = Database()
        booking = db.fetch_one("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        if not booking:
            db.close()
            return jsonify({"success": False, "message": "Booking not found"}), 404

        db.execute("UPDATE bookings SET payment_status = 'confirmed', status = 'confirmed' WHERE id = %s", (booking_id,))
        
        send_notification(booking["user_id"], "Payment Confirmed", f"Your payment for booking #{booking_id} has been verified and confirmed.")
        log_audit(session["user"]["id"], "Verify Payment", f"Booking #{booking_id}", "Verified QR payment")
        db.close()
        return jsonify({"success": True, "message": "Payment verified and booking confirmed"})

    @admin_required
    def api_refund_payment(self):
        if session["user"].get("role") == "staff":
            return jsonify({"success": False, "message": "Permission denied"}), 403

        data = request.json
        booking_id = data.get("booking_id")
        if not booking_id:
            return jsonify({"success": False, "message": "Booking ID required"}), 400

        db = Database()
        booking = db.fetch_one("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        if not booking:
            db.close()
            return jsonify({"success": False, "message": "Booking not found"}), 404

        db.execute("UPDATE bookings SET payment_status = 'refunded', status = 'cancelled' WHERE id = %s", (booking_id,))
        
        send_notification(booking["user_id"], "Refund Issued", f"A refund of NPR {booking['total']} has been issued for booking #{booking_id}.")
        log_audit(session["user"]["id"], "Refund Payment", f"Booking #{booking_id}", f"Refunded amount: NPR {booking['total']}")
        db.close()
        return jsonify({"success": True, "message": "Refund processed successfully"})

    @admin_required
    def api_manual_payment(self):
        data = request.json
        booking_id = data.get("booking_id")
        method = data.get("method", "Cash").strip()
        txn_ref = data.get("txn_code", "").strip()

        if not booking_id:
            return jsonify({"success": False, "message": "Booking ID required"}), 400

        db = Database()
        booking = db.fetch_one("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        if not booking:
            db.close()
            return jsonify({"success": False, "message": "Booking not found"}), 404

        db.execute(
            "UPDATE bookings SET payment_status = 'confirmed', status = 'confirmed', payment_method = %s, txn_code = %s WHERE id = %s",
            (method, txn_ref or f"MANUAL-{int(datetime.now().timestamp())}", booking_id)
        )
        
        send_notification(booking["user_id"], "Payment Confirmed", f"Your manual payment ({method}) for booking #{booking_id} has been recorded.")
        log_audit(session["user"]["id"], "Manual Payment Recorded", f"Booking #{booking_id}", f"Recorded manual payment via {method}")
        db.close()
        return jsonify({"success": True, "message": "Manual payment recorded successfully"})

    # ── USER MANAGEMENT ENDPOINTS ──────────────────────────────────────────
    @admin_required
    def api_users(self):
        db = Database()
        query = """
            SELECT id, name, email, role, status, created_at,
            (SELECT COUNT(*) FROM bookings WHERE user_id = users.id) AS bookings_count,
            (SELECT SUM(total) FROM bookings WHERE user_id = users.id AND status != 'cancelled') AS total_spent
            FROM users
            ORDER BY id DESC
        """
        users = db.fetch_all(query)
        db.close()
        return jsonify(users)

    @admin_required
    def api_user_detail(self, user_id):
        # Admin / Super Admin roles only. Staff cannot update roles/status or delete users.
        if session["user"].get("role") == "staff":
            return jsonify({"success": False, "message": "Permission denied"}), 403

        db = Database()
        user_row = db.fetch_one("SELECT id, role FROM users WHERE id = %s", (user_id,))
        if not user_row:
            db.close()
            return jsonify({"success": False, "message": "User not found"}), 404

        if request.method == "PUT":
            data = request.json
            name = data.get("name")
            email = data.get("email")
            role = data.get("role")
            status = data.get("status")

            # Prevent self-suspension or self-demotion
            if user_id == session["user"]["id"]:
                if status == "suspended" or role != session["user"]["role"]:
                    db.close()
                    return jsonify({"success": False, "message": "Self-modifying status or role is prohibited"}), 400

            # Super admin gate: only super_admin can modify other admins
            if user_row["role"] in ["admin", "super_admin"] and session["user"]["role"] != "super_admin" and user_id != session["user"]["id"]:
                db.close()
                return jsonify({"success": False, "message": "Only Super Admin can modify administrative users"}), 403

            # Update details
            db.execute(
                "UPDATE users SET name=%s, email=%s, role=%s, status=%s WHERE id=%s",
                (name, email, role, status, user_id)
            )
            log_audit(session["user"]["id"], "Update User Profile", f"User #{user_id}", f"Set role: {role}, status: {status}")
            db.close()
            return jsonify({"success": True, "message": "User updated successfully"})

        elif request.method == "DELETE":
            # Only super_admin can delete users
            if session["user"].get("role") != "super_admin":
                db.close()
                return jsonify({"success": False, "message": "Only Super Admin can delete user accounts"}), 403

            if user_id == session["user"]["id"]:
                db.close()
                return jsonify({"success": False, "message": "Self-deletion is prohibited"}), 400

            db.execute("DELETE FROM users WHERE id = %s", (user_id,))
            log_audit(session["user"]["id"], "Delete User Account", f"User #{user_id}", f"Permanently deleted account")
            db.close()
            return jsonify({"success": True, "message": "User deleted permanently"})

    # ── NOTIFICATIONS ENDPOINT ─────────────────────────────────────────────
    @admin_required
    def api_notifications(self):
        data = request.json
        user_id = data.get("user_id")
        title = data.get("title", "").strip()
        message = data.get("message", "").strip()

        if not user_id or not title or not message:
            return jsonify({"success": False, "message": "All message fields are required"}), 400

        send_notification(user_id, title, message)
        log_audit(session["user"]["id"], "Send Notification", f"User #{user_id}", f"Dispatched notification: {title}")
        return jsonify({"success": True, "message": "Notification sent successfully"})

    # ── AUDIT LOGS ENDPOINT ────────────────────────────────────────────────
    @admin_required
    def api_audit_logs(self):
        db = Database()
        logs = db.fetch_all("""
            SELECT a.*, u.name AS admin_name
            FROM audit_logs a
            LEFT JOIN users u ON a.admin_id = u.id
            ORDER BY a.id DESC
        """)
        db.close()
        return jsonify(logs)
