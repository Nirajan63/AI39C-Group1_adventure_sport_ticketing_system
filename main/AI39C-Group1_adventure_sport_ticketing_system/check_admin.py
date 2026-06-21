import os
from app.models.database import get_db_connection

def fetch_admin():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, email, password, must_change_password, status FROM users WHERE username = %s', ('Nirajan',))
    admin = cur.fetchone()
    print('ADMIN RECORD:', admin)
    conn.close()

if __name__ == '__main__':
    fetch_admin()
