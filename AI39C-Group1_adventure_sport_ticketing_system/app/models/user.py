from werkzeug.security import generate_password_hash, check_password_hash
from app.models.baseModel import BaseModel
from .data import Database

class User(BaseModel):
    @property
    def table(self):
        return "users"

    def __init__(self, name=None, email=None, password=None, role="user"):
        self.name = name
        self.email = email
        self.__password = None
        self.role = role

        if password:
            self.set_password(password)

    def set_password(self, plain_password):
        self.__password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        if self.__password is None:
            return False
        return check_password_hash(self.__password, plain_password)

    def save(self):
        db = Database()
        db.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (self.name, self.email, self.__password, self.role),
        )
        db.close()

    def update(self, user_id, update_password=False):
        db = Database()
        if update_password:
            db.execute(
                "UPDATE users SET username=%s, email=%s, password=%s, role=%s WHERE id=%s",
                (self.name, self.email, self.__password, self.role, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET username=%s, email=%s, role=%s WHERE id=%s",
                (self.name, self.email, self.role, user_id),
            )
        db.close()

    def update_profile(self, user_id, update_password=False):
        db = Database()
        if update_password:
            db.execute(
                "UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s",
                (self.name, self.email, self.__password, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET username=%s, email=%s WHERE id=%s",
                (self.name, self.email, user_id),
            )
        db.close()

    def email_exists(self, exclude_id=None):
        db = Database()
        if exclude_id:
            result = db.fetch_one(
                "SELECT id FROM users WHERE email = %s AND id != %s",
                (self.email, exclude_id),
            )
        else:
            result = db.fetch_one(
                "SELECT id FROM users WHERE email = %s", (self.email,)
            )
        db.close()
        return result is not None

    @classmethod
    def from_db(cls, data):
        if data is None:
            return None
        user = cls()
        user.name  = data.get("username") or data.get("name")
        user.email = data["email"]
        user._User__password = data["password"]
        user.role  = data["role"]
        return user

    def __str__(self):
        return f"User(username={self.name}, email={self.email}, role={self.role})"

    def __repr__(self):
        return f"<User email={self.email}>"
