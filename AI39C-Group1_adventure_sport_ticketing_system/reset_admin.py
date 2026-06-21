import os
from werkzeug.security import generate_password_hash
from app.models.database import get_db_connection

def reset_admin(username='Nirajan', email='admin@sportadventure.com', new_password='Nirajan@123'):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = generate_password_hash(new_password)
    # Try updating by username first
    cursor.execute("UPDATE users SET password=%s, must_change_password=0 WHERE username=%s", (hashed, username))
    if cursor.rowcount == 0:
        # fallback to email
        cursor.execute("UPDATE users SET password=%s, must_change_password=0 WHERE email=%s", (hashed, email))
    conn.commit()
    conn.close()
    print(f"Admin credentials reset for {username}/{email}.")

if __name__ == '__main__':
    reset_admin()
