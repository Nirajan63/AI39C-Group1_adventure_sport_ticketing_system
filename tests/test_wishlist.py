from app import create_app
import pytest


# =========================
# FIXTURE
# =========================
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client
