from app.models.database import get_db_connection, init_db

class Database:
    def __init__(self):
        self._connection = get_db_connection()

    def fetch_one(self, query, params=None):
        cursor = self._connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        cursor = self._connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results

    def execute(self, query, params=None):
        cursor = self._connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self._connection.commit()
        cursor.close()

    def close(self):
        if self._connection:
            self._connection.close()

    @staticmethod
    def create_tables():
        init_db()
