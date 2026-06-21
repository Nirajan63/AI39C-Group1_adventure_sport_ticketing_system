from flask import render_template, request, session, redirect, url_for, flash
from datetime import datetime
from app.controlers.baseController import BaseController
from app.models.user import User
from app.models.data import Database


# ── Activities Metadata Definition ────────────────────────────────────────
ACTIVITIES = {
    "paragliding": {
        "name": "Paragliding",
        "price": 4500.0,
        "location": "Pokhara",
        "duration": "1 hour",
        "img": "Paragliding.png",
        "pic": "Paragliding_Pic.jpg"
    },
    "bungee": {
        "name": "Bungee Jumping",
        "price": 6500.0,
        "location": "Bhote Koshi",
        "duration": "30 mins",
        "img": "Bungee-jumping.png",
        "pic": "BungeeJump_Pic.jpg"
    },
    "rafting": {
        "name": "White Water Rafting",
        "price": 3500.0,
        "location": "Trishuli",
        "duration": "4 hours",
        "img": "Rafting.png",
        "pic": "Rafting_Pic.jpg"
    },
    "trekking": {
        "name": "Trekking",
        "price": 2500.0,
        "location": "Annapurna",
        "duration": "2 days",
        "img": "Trekking_.png",
        "pic": "Trekking_Pic.jpeg"
    },
    "canyoning": {
        "name": "Canyoning",
        "price": 5000.0,
        "location": "Jalbire",
        "duration": "5 hours",
        "img": "Canyoning.png",
        "pic": "Canyoning_Pic.jpg"
    },
    "ziplining": {
        "name": "Zip-lining",
        "price": 2000.0,
        "location": "Chitwan",
        "duration": "2 hours",
        "img": "Zip_lining.png",
        "pic": "ZipLining_Pic.jpg"
    }
}


class AuthController(BaseController):

    def __init__(self):
        # FIX: initialise user_model so self.user_model.find_by() works
        self.user_model = User()

    # ── LOGIN ──────────────────────────────────────────────────────────────
    def login(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            # FIX: form sends name="username", not name="email"
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                flash("Username and password are required.", "danger")
                return render_template("Login.html")

            # Support login by email OR username
            user_data = self.user_model.find_by("email", username)
            if not user_data:
                user_data = self.user_model.find_by("name", username)

            if user_data:
                user = User.from_db(user_data)
                if user.check_password(password):
                    # FIX: store as session["user"] dict (dashboard reads this key)
                    # FIX: include "username" alias because Dashboard.html uses user.username
                    session["user"] = {
                        "id":       user_data["id"],
                        "name":     user_data["name"],
                        "username": user_data["name"],   # alias for template
                        "email":    user_data["email"],
                        "role":     user_data["role"],
                        "joined":   "May 2026",
                    }
                    return self.flash_and_redirect(
                        "Login successful!", "success", "auth.dashboard"
                    )

            flash("Invalid username/email or password.", "danger")

        return render_template("Login.html")

    # ── REGISTER ───────────────────────────────────────────────────────────
    def register(self):
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email    = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            if not username or not email or not password:
                flash("All fields are required!")
                return render_template("Register.html", error="All fields are required!")

            u = User(name=username, email=email, password=password)
            if u.email_exists():
                flash("Email is already registered!")
                return render_template("Register.html", error="Email already registered!")

            try:
                u.save()
                flash("Registration successful! Please log in.")
                return redirect(url_for("auth.login"))
            except Exception as e:
                print("Registration error:", e)
                flash("An error occurred during registration.")
                return render_template("Register.html", error="Registration failed.")

        return render_template("Register.html")

    # ── LOGOUT ─────────────────────────────────────────────────────────────
    def logout(self):
        session.clear()
        return redirect(url_for("auth.login"))

    # ── DASHBOARD ──────────────────────────────────────────────────────────
    def dashboard(self):
        # FIX: guard uses session["user"] (consistent with login)
        if "user" not in session:
            return redirect(url_for("auth.login"))

        user    = session["user"]
        user_id = user["id"]

        # FIX: ensure "username" and "joined" are always present
        # (guards against old sessions that were created before the fix)
        if "username" not in user:
            user["username"] = user.get("name", "Adventurer")
        if "joined" not in user:
            user["joined"] = "May 2026"

        # 1. Fetch bookings from SQLite
        db = Database()
        bookings_data = db.fetch_all(
            "SELECT * FROM bookings WHERE user_id = %s ORDER BY id DESC", (user_id,)
        )
        db.close()

        # 2. Enrich bookings with display metadata
        bookings_list = []
        for b in bookings_data:
            b_dict   = dict(b)
            act_name = b_dict.get("activity", "").strip().lower()

            act_key = None
            for key, val in ACTIVITIES.items():
                if val["name"].lower() == act_name or key == act_name:
                    act_key = key
                    break

            if act_key:
                act = ACTIVITIES[act_key]
                b_dict["img"]      = act["img"]
                b_dict["location"] = act["location"]
                b_dict["duration"] = act["duration"]
            else:
                b_dict["img"]      = "Mountain-Main.png"
                b_dict["location"] = "Nepal"
                b_dict["duration"] = "1 day"

            bookings_list.append(b_dict)

        # 3. Calculate live metrics
        stats = {
            "total":     len(bookings_list),
            "upcoming":  sum(1 for b in bookings_list if b["status"] == "confirmed"),
            "completed": sum(1 for b in bookings_list if b["status"] == "completed"),
            "spent":     sum(int(b.get("total", 0)) for b in bookings_list),
        }

        return render_template(
            "Dashboard.html",
            user=user,
            stats=stats,
            bookings=bookings_list,
            activities=ACTIVITIES
        )

    # ── BOOK ACTIVITY ──────────────────────────────────────────────────────
    def book_activity(self):
        if "user" not in session:
            return redirect(url_for("auth.login"))

        if request.method == "POST":
            activity_id = request.form.get("activity_id", "").strip().lower()
            date        = request.form.get("date", "")
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

            price         = float(act["price"])
            total         = price * people
            activity_name = act["name"]

            user    = session["user"]
            user_id = user["id"]

            if date:
                db = Database()
                try:
                    db.execute(
                        "INSERT INTO bookings (user_id, activity, date, people, price, total, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (user_id, activity_name, date, people, price, total, "confirmed")
                    )
                    flash(f"🎉 {activity_name} booked successfully!")
                except Exception as e:
                    print("Error saving booking:", e)
                    flash("An error occurred. Please try again.")
                db.close()

        return redirect(url_for("auth.dashboard"))