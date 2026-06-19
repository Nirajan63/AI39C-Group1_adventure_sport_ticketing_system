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
# TEST 1: HOME PAGE LOADS
# =========================
def test_home_page_status(client):
    response = client.get("/")

    assert response.status_code == 200
# =========================
# TEST 2: HOME PAGE CONTENT
# =========================
def test_home_page_content(client):
    response = client.get("/")

    html = response.data

    assert b"Thrill Sphere" in html
    assert b"Adventure" in html
    assert b"Explore" in html

# =========================
# TEST 3: HERO SECTION EXISTS
# =========================
def test_hero_section_exists(client):
    response = client.get("/")

    assert b"hero" in response.data.lower()

# =========================
# TEST 3: HERO SECTION EXISTS
# =========================
def test_hero_section_exists(client):
    response = client.get("/")

    assert b"hero" in response.data.lower()



