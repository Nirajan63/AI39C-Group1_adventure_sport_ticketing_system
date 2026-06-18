from app.models.user import User

def test_user_creation():
    user = User("Salina", "salina@gmail.com")

    assert user.name == "Salina"
    assert user.email == "salina@gmail.com"