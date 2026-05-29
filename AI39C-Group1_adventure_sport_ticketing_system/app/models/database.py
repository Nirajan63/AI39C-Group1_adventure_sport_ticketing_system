
import pymysql
from app.config import Config

def get_db_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def init_db():
    try:
        conn = get_db_connection()
        conn.close()
        print("MySQL database connection tested and verified successfully.")
    except Exception as e:
        print("Database connection verification failed:", e)

