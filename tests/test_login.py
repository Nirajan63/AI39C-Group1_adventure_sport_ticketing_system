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
# =========================

# TEST 2: LOGIN ROUTE ACCEPTS POST (basic check)
# =========================
def test_login_post_route(client):
    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpass"
    })
# =========================
# TEST 3: test invalid login submission
# =========================
    response = client.post(
        "/login",
        data={
            "username": "wronguser",
            "password": "wrongpass"
        },
        follow_redirects=True
    )

    assert response.status_code == 200