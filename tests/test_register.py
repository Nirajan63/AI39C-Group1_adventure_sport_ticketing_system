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

# =========================
# TEST 1: REGISTER PAGE LOADS
# =========================
def test_register_page_status(client):
    response = client.get("/register")

    assert response.status_code == 200
# =========================
# TEST 2: REGISTER FORM EXISTS
# =========================
def test_register_form_exists(client):
    response = client.get("/register")
    html = response.data.lower()

    assert b"registration" in html
    assert b"username" in html
    assert b"email" in html
    assert b"password" in html
# =========================
# TEST 3: FORM ELEMENT CHECK
# =========================
def test_register_form_structure(client):
    response = client.get("/register")

    html = response.data.lower()

    assert b"signup-form" in html
    assert b"input-box" in html

# =========================
# TEST 4: LOGIN LINK EXISTS
# =========================
def test_login_link_exists(client):
    response = client.get("/register")

    assert b"/login" in response.data
