from app.models.database import get_db_connection

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, email, role, status FROM users')
    rows = cur.fetchall()
    print("USERS IN DATABASE:")
    for r in rows:
        print(r)
    conn.close()

if __name__ == '__main__':
    main()
