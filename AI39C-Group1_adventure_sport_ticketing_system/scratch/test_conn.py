import pymysql

passwords = ["", "root", "admin", "1234", "123456", "mysql", "password"]
for pw in passwords:
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password=pw,
            port=3306
        )
        print(f"SUCCESS: Connected with password: '{pw}'")
        conn.close()
        break
    except Exception as e:
        print(f"FAILED with password '{pw}': {e}")
