from werkzeug.security import generate_password_hash
from app.models.database import get_db_connection

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    hashed = generate_password_hash('admin123')
    cur.execute("UPDATE users SET password=%s, must_change_password=0 WHERE username='admin'", (hashed,))
    conn.commit()
    conn.close()
    print("Successfully set password for username 'admin' to 'admin123' and disabled force pw change.")

if __name__ == '__main__':
    main()
