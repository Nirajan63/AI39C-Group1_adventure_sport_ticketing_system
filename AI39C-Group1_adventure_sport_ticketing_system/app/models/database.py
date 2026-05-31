
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
    
    # Insert test user if missing
    cursor.execute('SELECT * FROM users WHERE username = ?', ('testuser',))
    if not cursor.fetchone():
        cursor.execute(
            '''INSERT INTO users (username, email, password, first_name, last_name, role) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            ('testuser', 'test@example.com', 'password123', 'Test', 'User', 'Adventure Seeker')
        )
        
    conn.commit()
    conn.close()

