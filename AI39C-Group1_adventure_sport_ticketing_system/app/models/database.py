
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sportadventure.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # If the database exists but the users table lacks the profile fields (e.g., first_name),
    # drop/recreate to handle the schema update smoothly.
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT first_name FROM users LIMIT 1")
            conn.close()
        except sqlite3.OperationalError:
            conn.close()
            try:
                os.remove(DB_PATH)
                print("Deleted outdated SQLite database to apply new schema changes.")
            except Exception as e:
                print("Error removing outdated database file:", e)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table with all profile properties
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            city TEXT,
            bio TEXT,
            language TEXT DEFAULT 'en',
            role TEXT DEFAULT 'Adventure Seeker',
            avatar TEXT,
            cover TEXT,
            theme_preference TEXT DEFAULT 'light',
            status TEXT DEFAULT 'active',
            must_change_password INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity TEXT NOT NULL,
            date TEXT NOT NULL,
            people INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'confirmed',
            payment_status TEXT DEFAULT 'pending',
            payment_method TEXT,
            txn_code TEXT,
            internal_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create wishlist table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create activities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            price REAL,
            duration TEXT,
            capacity INTEGER,
            img TEXT,
            pic TEXT,
            location TEXT,
            difficulty TEXT,
            status TEXT DEFAULT 'active',
            available_dates TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create audit_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            action TEXT,
            target_record TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            message TEXT,
            status TEXT DEFAULT 'unread',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if we need to apply migrations to existing tables
    # Alter users table to add status and must_change_password
    try:
        cursor.execute("SELECT status FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
        cursor.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0")

    # Alter bookings table to add payment columns
    try:
        cursor.execute("SELECT payment_status FROM bookings LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE bookings ADD COLUMN payment_status TEXT DEFAULT 'pending'")
        cursor.execute("ALTER TABLE bookings ADD COLUMN payment_method TEXT")
        cursor.execute("ALTER TABLE bookings ADD COLUMN txn_code TEXT")
        cursor.execute("ALTER TABLE bookings ADD COLUMN internal_notes TEXT")
    
    # Insert test user if missing
    cursor.execute('SELECT * FROM users WHERE username = ?', ('testuser',))
    if not cursor.fetchone():
        cursor.execute(
            '''INSERT INTO users (username, email, password, first_name, last_name, role) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            ('testuser', 'test@example.com', 'password123', 'Test', 'User', 'Adventure Seeker')
        )
        
    # Seed default admin user if missing
    cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', ('admin', 'admin@sportadventure.com'))
    if not cursor.fetchone():
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash('admin123')
        cursor.execute(
            '''INSERT INTO users (username, email, password, first_name, last_name, role, status, must_change_password) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ('admin', 'admin@sportadventure.com', hashed_password, 'System', 'Admin', 'super_admin', 'active', 1)
        )
        
    # Prepopulate activities if table is empty
    cursor.execute('SELECT COUNT(*) AS count FROM activities')
    if cursor.fetchone()[0] == 0:
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

    conn.commit()
    conn.close()

