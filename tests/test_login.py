from app import create_app
import pytest


# =========================
# FIXTURE (REUSABLE APP)
# =========================
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client
# =========================
# TEST 1: LOGIN PAGE LOADS
# =========================
def test_login_page_status(client):
    response = client.get("/login")

    assert response.status_code == 200




    