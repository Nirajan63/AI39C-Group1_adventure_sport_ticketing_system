import pymysql
import pymysql.cursors
import os
from app.config import Config  # Ensure .env is loaded

class SafeDictCursor(pymysql.cursors.DictCursor):
    def execute(self, query, args=None):
        if query and '?' in query:
            query = query.replace('?', '%s')
        super().execute(query, args)
        return self

def get_db_connection():
    host = os.environ.get("MYSQL_HOST", "localhost")
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    db_name = os.environ.get("MYSQL_DB", "sportadventure")
    port = int(os.environ.get("MYSQL_PORT", 3306))
    
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        port=port,
        cursorclass=SafeDictCursor
    )
    return conn


def _normalize_event_row(row):
    """Ensure PyMySQL datetime values serialize consistently for JSON/API consumers."""
    if not row:
        return row
    d = dict(row)
    dt = d.get("date_time")
    if dt is not None:
        if hasattr(dt, "strftime"):
            d["date_time"] = dt.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            s = str(dt).strip()
            if "T" not in s and " " in s:
                s = s.replace(" ", "T", 1)
            d["date_time"] = s[:19] if len(s) >= 19 else s
    return d

def create_database_if_not_exists():
    host = os.environ.get("MYSQL_HOST", "localhost")
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    port = int(os.environ.get("MYSQL_PORT", 3306))
    db_name = os.environ.get("MYSQL_DB", "sportadventure")
    
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    conn.commit()
    cursor.close()
    conn.close()

def init_db():
    create_database_if_not_exists()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table with all profile properties
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            phone VARCHAR(50),
            city VARCHAR(100),
            bio TEXT,
            language VARCHAR(50) DEFAULT 'en',
            role VARCHAR(50) DEFAULT 'Adventure Seeker',
            avatar TEXT,
            cover TEXT,
            theme_preference VARCHAR(50) DEFAULT 'light',
            status VARCHAR(50) DEFAULT 'active',
            must_change_password INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            activity VARCHAR(255) NOT NULL,
            date VARCHAR(50) NOT NULL,
            people INT NOT NULL,
            price DOUBLE NOT NULL,
            total DOUBLE NOT NULL,
            status VARCHAR(50) DEFAULT 'confirmed',
            payment_status VARCHAR(50) DEFAULT 'pending',
            payment_method VARCHAR(50),
            txn_code VARCHAR(100),
            internal_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create wishlist table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wishlist (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            activity_id VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Create activities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id VARCHAR(100) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            price DOUBLE,
            duration VARCHAR(100),
            capacity INT,
            img VARCHAR(255),
            pic VARCHAR(255),
            location VARCHAR(255),
            difficulty VARCHAR(50),
            status VARCHAR(50) DEFAULT 'active',
            available_dates TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create audit_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admin_id INT,
            action VARCHAR(255),
            target_record VARCHAR(255),
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255),
            message TEXT,
            status VARCHAR(50) DEFAULT 'unread',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Create posts table (Gallery)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admin_id INT,
            title VARCHAR(255),
            image_url VARCHAR(255),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Create reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            activity VARCHAR(255),
            rating INT DEFAULT 5,
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Check if we need to apply migrations to existing tables
    # Alter users table to add status and must_change_password
    try:
        cursor.execute("SELECT status FROM users LIMIT 1")
    except Exception:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN status VARCHAR(50) DEFAULT 'active'")
            cursor.execute("ALTER TABLE users ADD COLUMN must_change_password INT DEFAULT 0")
        except Exception:
            pass

    # Alter bookings table to add payment columns
    try:
        cursor.execute("SELECT payment_status FROM bookings LIMIT 1")
    except Exception:
        try:
            cursor.execute("ALTER TABLE bookings ADD COLUMN payment_status VARCHAR(50) DEFAULT 'pending'")
            cursor.execute("ALTER TABLE bookings ADD COLUMN payment_method VARCHAR(50)")
            cursor.execute("ALTER TABLE bookings ADD COLUMN txn_code VARCHAR(100)")
            cursor.execute("ALTER TABLE bookings ADD COLUMN internal_notes TEXT")
        except Exception:
            pass
    
    # Insert test user if missing
    cursor.execute('SELECT * FROM users WHERE username = ?', ('testuser',))
    if not cursor.fetchone():
        cursor.execute(
            '''INSERT INTO users (username, email, password, first_name, last_name, role) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            ('testuser', 'test@example.com', 'password123', 'Test', 'User', 'Adventure Seeker')
        )
        
    # Seed default admin user if missing
    cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', ('Nirajan', 'admin@sportadventure.com'))
    if not cursor.fetchone():
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash('Nirajan@123')
        cursor.execute(
            '''INSERT INTO users (username, email, password, first_name, last_name, role, status, must_change_password) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ('Nirajan', 'admin@sportadventure.com', hashed_password, 'System', 'Admin', 'super_admin', 'active', 1)
        )
        
    # Prepopulate activities if table is empty
    cursor.execute('SELECT COUNT(*) AS count FROM activities')
    if cursor.fetchone()['count'] == 0:
        default_activities = [
            ("paragliding", "Paragliding", "Experience the thrill of flying like a bird over Pokhara.", "Sky", 4500.0, "1 hour", 10, "Paragliding.png", "Paragliding_Pic.jpg", "Pokhara", "Medium"),
            ("bungee", "Bungee Jumping", "A heart-pounding plunge over the wild Bhote Koshi River.", "Extreme", 6500.0, "30 mins", 15, "Bungee-jumping.png", "BungeeJump_Pic.jpg", "Bhote Koshi", "Hard"),
            ("rafting", "White Water Rafting", "Ride the thrilling rapids of the Trishuli River.", "Water", 3500.0, "4 hours", 20, "Rafting.png", "Rafting_Pic.jpg", "Trishuli", "Medium"),
            ("trekking", "Trekking", "Hike through the gorgeous Annapurna range.", "Mountain", 2500.0, "2 days", 15, "Trekking_.png", "Trekking_Pic.jpeg", "Annapurna", "Medium"),
            ("canyoning", "Canyoning", "Abseil, slide and jump down wet canyon walls.", "Extreme", 5000.0, "5 hours", 10, "Canyoning.png", "Canyoning_Pic.jpg", "Jalbire", "Hard"),
            ("ziplining", "Zip-lining", "Glide high above the forests of Chitwan.", "Aerial", 2000.0, "2 hours", 20, "Zip_lining.png", "ZipLining_Pic.jpg", "Chitwan", "Easy")
        ]
        for act in default_activities:
            cursor.execute(
                '''INSERT INTO activities (id, name, description, category, price, duration, capacity, img, pic, location, difficulty, status, available_dates)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', '')''',
                act
            )

    # Create events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            date_time VARCHAR(100) NOT NULL,
            location VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL,
            price INT NOT NULL DEFAULT 0,
            tickets_left INT DEFAULT 50,
            image_url VARCHAR(255),
            badge VARCHAR(100),
            duration VARCHAR(100) DEFAULT '3 hours',
            is_published INT DEFAULT 1,
            organizer_name VARCHAR(255) DEFAULT 'Thrill Sphere Organizer',
            organizer_phone VARCHAR(50) DEFAULT '+977-9876543210',
            organizer_email VARCHAR(100) DEFAULT 'organizer@thrillsphere.com',
            latitude DOUBLE,
            longitude DOUBLE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed events if empty
    cursor.execute("SELECT COUNT(*) AS count FROM events")
    if cursor.fetchone()["count"] == 0:
        from datetime import datetime, timedelta
        now = datetime.now()
        
        # Calculate next Wednesday
        days_to_wed = (2 - now.weekday()) % 7
        if days_to_wed == 0:
            days_to_wed = 7
        next_wednesday = now + timedelta(days=days_to_wed)
        
        # Calculate next Saturday
        days_to_sat = (5 - now.weekday()) % 7
        if days_to_sat == 0:
            days_to_sat = 7
        next_saturday = now + timedelta(days=days_to_sat)
        
        # Calculate next Sunday
        days_to_sun = (6 - now.weekday()) % 7
        if days_to_sun == 0:
            days_to_sun = 7
        next_sunday = now + timedelta(days=days_to_sun)

        # Formatted dates
        today_str = now.replace(hour=10, minute=0, second=0).isoformat()
        tomorrow_str = (now + timedelta(days=1)).replace(hour=14, minute=0, second=0).isoformat()
        wednesday_str = next_wednesday.replace(hour=8, minute=30, second=0).isoformat()
        saturday_str = next_saturday.replace(hour=7, minute=0, second=0).isoformat()
        sunday_str = next_sunday.replace(hour=9, minute=0, second=0).isoformat()
        next_week_str = (now + timedelta(days=8)).replace(hour=10, minute=0, second=0).isoformat()

        demo_events = [
            (
                "Annapurna Trekking Expedition",
                "Embark on a magnificent journey through the Annapurna foothills, experiencing scenic local villages and beautiful Himalayan peaks.",
                wednesday_str,
                "Annapurna",
                "Adventure",
                4500,
                8,
                "Trekking_Pic.jpeg",
                "Featured",
                "2 days",
                "Annapurna Mountain Club",
                "+977-9801234567",
                "info@annapurnatreks.org.np",
                28.5961,
                83.8203
            ),
            (
                "Pokhara Paragliding Championship",
                "Watch or participate in the annual aero-sports tournament gliding over the scenic Phewa Lake with mountain backdrops.",
                today_str,
                "Pokhara",
                "Adventure",
                5000,
                10,
                "Paragliding_Pic.jpg",
                "Trending",
                "4 hours",
                "Pokhara Aero Sports Association",
                "+977-9811223344",
                "fly@pokharaglide.com",
                28.2096,
                83.9856
            ),
            (
                "Nagarjun Rock Climbing & Hiking",
                "A weekend workshop and social meetup for climbing and hiking enthusiasts of all skill levels. Safety gear and training included.",
                saturday_str,
                "Kathmandu",
                "Adventure",
                1200,
                15,
                "Canyoning_Pic.jpg",
                "Popular",
                "6 hours",
                "Nagarjun Adventure Guides",
                "+977-9841556677",
                "climb@nagarjun.com",
                27.7172,
                85.3240
            ),
            (
                "Trishuli White Water Challenge",
                "Conquer the thrilling rapids of the Trishuli River in a massive group rafting race. Includes barbecue lunch.",
                sunday_str,
                "Trishuli",
                "Water Sports",
                3500,
                25,
                "Rafting_Pic.jpg",
                "Popular",
                "5 hours",
                "Trishuli River Rafting Co.",
                "+977-9807766554",
                "raft@trishulirapids.com",
                27.8000,
                85.1333
            ),
            (
                "Bhote Koshi Bungee Carnival",
                "Leap from the suspension bridge 160 meters above the wild Bhote Koshi River. The ultimate adrenaline rush.",
                next_week_str,
                "Bhote Koshi",
                "Adventure",
                6500,
                2,
                "BungeeJump_Pic.jpg",
                "Featured",
                "2 hours",
                "The Last Resort Nepal",
                "+977-1-4434321",
                "bungee@lastresort.com.np",
                27.7667,
                85.8833
            ),
            (
                "Kathmandu Music Festival",
                "Join Nepal's biggest outdoor music gathering featuring top local bands and electronic music artists under the stars.",
                tomorrow_str,
                "Kathmandu",
                "Music",
                1500,
                45,
                "Mountain-Main.png",
                "Trending",
                "6 hours",
                "K-Town Sound Events",
                "+977-9851010101",
                "tickets@ktmfest.com",
                27.7172,
                85.3240
            ),
            (
                "Chitwan Zip-Line & BBQ Fest",
                "Zipline over the forest canopy at high speed, followed by a jungle-style barbecue dinner party and campfire.",
                (now + timedelta(days=4)).replace(hour=11, minute=0, second=0).isoformat(),
                "Chitwan",
                "Adventure",
                2000,
                3,
                "ZipLining_Pic.jpg",
                "Trending",
                "3 hours",
                "Chitwan Canopy Adventures",
                "+977-9860123456",
                "info@chitwanzip.com",
                27.5260,
                84.4503
            ),
            (
                "Lakeside Jazz Night",
                "A cozy acoustic jazz performance by the lake. Free mocktail/drink included with every ticket.",
                (now + timedelta(days=10)).replace(hour=19, minute=30, second=0).isoformat(),
                "Pokhara",
                "Music",
                800,
                30,
                "Paragliding_Pic.jpg",
                "Popular",
                "3 hours",
                "Lakeside Acoustic Club",
                "+977-9818989898",
                "jazz@lakesidepokhara.com",
                28.2096,
                83.9856
            )
        ]
        for evt in demo_events:
            cursor.execute(
                """
                INSERT INTO events (title, description, date_time, location, category, price, tickets_left, image_url, badge, duration, organizer_name, organizer_phone, organizer_email, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                evt
            )

    # ── Referral Codes Table ──────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referral_codes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            code VARCHAR(20) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # ── Referrals Table ───────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            referrer_id INT NOT NULL,
            referred_user_id INT NOT NULL,
            status VARCHAR(30) DEFAULT 'joined',
            reward_earned INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referrer_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (referred_user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


# ── Referral Helper Functions ─────────────────────────────────────────────────

def generate_referral_code(user_id, username):
    """Generate and store a unique referral code for a user."""
    import string, random as _random
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already has a code
    cursor.execute("SELECT code FROM referral_codes WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row["code"]

    # Generate unique code: TS + first 4 chars of username + 4 random alphanum
    prefix = ''.join(c.upper() for c in username[:4] if c.isalpha())
    suffix = ''.join(_random.choices(string.ascii_uppercase + string.digits, k=4))
    code = f"TS{prefix}{suffix}"

    # Ensure uniqueness
    attempts = 0
    while attempts < 10:
        cursor.execute("SELECT id FROM referral_codes WHERE code = ?", (code,))
        if not cursor.fetchone():
            break
        suffix = ''.join(_random.choices(string.ascii_uppercase + string.digits, k=4))
        code = f"TS{prefix}{suffix}"
        attempts += 1

    try:
        cursor.execute(
            "INSERT INTO referral_codes (user_id, code) VALUES (?, ?)",
            (user_id, code)
        )
        conn.commit()
    except Exception:
        # Race condition: fetch existing
        cursor.execute("SELECT code FROM referral_codes WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        code = row["code"] if row else code

    conn.close()
    return code


def get_referral_stats(user_id):
    """Return all referral statistics for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # All referrals made by this user
    cursor.execute("""
        SELECT r.*, u.username, u.created_at AS user_joined
        FROM referrals r
        JOIN users u ON r.referred_user_id = u.id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    referred_users = []
    total_earned = 0
    pending_earnings = 0
    pending_count = 0
    successful = 0

    for row in rows:
        status = row["status"]
        reward = int(row.get("reward_earned") or 0)
        joined_date = row["user_joined"]
        if hasattr(joined_date, "strftime"):
            joined_date = joined_date.strftime("%b %d, %Y")
        else:
            joined_date = str(joined_date)[:10] if joined_date else "N/A"

        if status == "booked":
            total_earned += reward
            successful += 1
        elif status == "joined":
            pending_count += 1
            pending_earnings += 750  # base pending reward estimate

        referred_users.append({
            "username": row["username"],
            "status": status,
            "joined_date": joined_date,
        })

    # Determine tier
    if successful >= 11:
        tier_emoji, tier_label, per_reward, next_tier_at = "💎", "Platinum", 2000, successful + 5
    elif successful >= 6:
        tier_emoji, tier_label, per_reward, next_tier_at = "🥇", "Gold", 1500, 11
    elif successful >= 3:
        tier_emoji, tier_label, per_reward, next_tier_at = "🥈", "Silver", 1000, 6
    else:
        tier_emoji, tier_label, per_reward, next_tier_at = "🥉", "Bronze", 750, 3

    stats = {
        "total_invited": len(rows),
        "successful": successful,
        "pending": pending_count,
        "total_earned": total_earned,
        "pending_earnings": pending_earnings,
        "per_referral_reward": per_reward,
        "current_tier_emoji": tier_emoji,
        "current_tier_label": tier_label,
        "next_tier_at": next_tier_at,
    }

    return stats, referred_users


def record_referral(referrer_code, new_user_id):
    """Called after a new user registers via a referral link/code."""
    if not referrer_code:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM referral_codes WHERE code = ?", (referrer_code,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return
        referrer_id = row["user_id"]
        if referrer_id == new_user_id:
            conn.close()
            return

        # Check not already recorded
        cursor.execute(
            "SELECT id FROM referrals WHERE referrer_id = ? AND referred_user_id = ?",
            (referrer_id, new_user_id)
        )
        if cursor.fetchone():
            conn.close()
            return

        cursor.execute(
            "INSERT INTO referrals (referrer_id, referred_user_id, status, reward_earned) VALUES (?, ?, 'joined', 0)",
            (referrer_id, new_user_id)
        )
        conn.commit()
    except Exception as e:
        print(f"record_referral error: {e}")
    finally:
        conn.close()


def mark_referral_booked(user_id):
    """When a referred user completes their first booking, upgrade referral to booked."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, referrer_id FROM referrals WHERE referred_user_id = ? AND status = 'joined'",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return

        referral_id = row["id"]
        referrer_id = row["referrer_id"]

        # Calculate reward based on referrer tier
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM referrals WHERE referrer_id = ? AND status = 'booked'",
            (referrer_id,)
        )
        cnt_row = cursor.fetchone()
        completed = int(cnt_row["cnt"]) if cnt_row else 0

        if completed >= 10:
            reward = 2000
        elif completed >= 5:
            reward = 1500
        elif completed >= 2:
            reward = 1000
        else:
            reward = 750

        cursor.execute(
            "UPDATE referrals SET status = 'booked', reward_earned = ? WHERE id = ?",
            (reward, referral_id)
        )
        conn.commit()
    except Exception as e:
        print(f"mark_referral_booked error: {e}")
    finally:
        conn.close()

def get_event_by_id(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    return _normalize_event_row(event)

def get_published_events(filters, page=1, per_page=6):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM events WHERE is_published = 1"
    params = []

    if filters.get("category"):
        query += " AND category = ?"
        params.append(filters["category"])

    if filters.get("location"):
        query += " AND location = ?"
        params.append(filters["location"])

    if filters.get("search"):
        query += " AND (title LIKE ? OR description LIKE ?)"
        search_val = f"%{filters['search']}%"
        params.extend([search_val, search_val])

    if filters.get("price_max"):
        try:
            query += " AND price <= ?"
            params.append(int(filters["price_max"]))
        except ValueError:
            pass

    if filters.get("date_start"):
        query += " AND DATE(date_time) >= DATE(?)"
        params.append(filters["date_start"])
    if filters.get("date_end"):
        query += " AND DATE(date_time) <= DATE(?)"
        params.append(filters["date_end"])

    sort_by = filters.get("sort_by")
    if sort_by == "price_asc":
        query += " ORDER BY price ASC"
    elif sort_by == "price_desc":
        query += " ORDER BY price DESC"
    elif sort_by == "popularity":
        query += " ORDER BY tickets_left ASC"
    elif sort_by == "upcoming":
        query += " ORDER BY date_time ASC"
    else:
        query += " ORDER BY date_time ASC"

    # Count total matched — strip ORDER BY before wrapping in subquery (MySQL doesn't allow it)
    count_base = query.split(" ORDER BY")[0]
    count_query = f"SELECT COUNT(*) as count FROM ({count_base}) AS temp_count"
    cursor.execute(count_query, params)
    row = cursor.fetchone()
    total_events = row["count"] if row else 0

    # Paginate
    query += " LIMIT ? OFFSET ?"
    params.extend([int(per_page), int((page - 1) * per_page)])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    events_list = [_normalize_event_row(row) for row in rows]

    import math
    total_pages = math.ceil(total_events / per_page)

    return {
        "events": events_list,
        "page": page,
        "per_page": per_page,
        "total_events": total_events,
        "total_pages": max(total_pages, 1)
    }

def get_featured_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM events WHERE is_published = 1 AND badge IN ('Featured', 'Trending', 'Popular') LIMIT 4"
    )
    rows = cursor.fetchall()
    conn.close()
    return [_normalize_event_row(r) for r in rows]

def get_distinct_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM events WHERE is_published = 1 ORDER BY category")
    rows = cursor.fetchall()
    conn.close()
    return [r["category"] for r in rows]

def get_distinct_locations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT location FROM events WHERE is_published = 1 ORDER BY location")
    rows = cursor.fetchall()
    conn.close()
    return [r["location"] for r in rows]

import random
def create_booking(user_id, activity_id, booking_date, people):
    try:
        people_val = int(people)
        if people_val < 1:
            return None
    except (ValueError, TypeError):
        return None

    if activity_id and activity_id.startswith("event_"):
        event_id = int(activity_id.split("_")[1])
        event = get_event_by_id(event_id)
        if not event or event["tickets_left"] < people_val:
            return None
        
        total = event["price"] * people_val
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Decrement tickets_left
        cursor.execute(
            "UPDATE events SET tickets_left = tickets_left - ? WHERE id = ?",
            (people_val, event_id)
        )
        
        # Insert booking with direct payment
        cursor.execute(
            """
            INSERT INTO bookings (
                user_id, activity, date, people, price, total, status, payment_status, payment_method, txn_code, internal_notes
            ) VALUES (?, ?, ?, ?, ?, ?, 'confirmed', 'confirmed', 'direct', ?, ?)
            """,
            (
                user_id,
                event["title"],
                booking_date,
                people_val,
                event["price"],
                total,
                f"TXN-EVT-{random.randint(100000, 999999)}",
                f"event_{event_id}"
            ),
        )
        conn.commit()
        booking_id = cursor.lastrowid
        
        try:
            cursor.execute(
                "INSERT INTO notifications (user_id, title, message, status) VALUES (?, ?, ?, 'unread')",
                (
                    user_id,
                    "Booking Confirmed",
                    f"Your booking for event '{event['title']}' on {booking_date} has been confirmed successfully!"
                )
            )
            conn.commit()
        except Exception as notif_err:
            print("Error creating event booking notification:", notif_err)
            
        conn.close()
        return booking_id
    return None