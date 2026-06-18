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
# TEST 1: WISHLIST PAGE LOADS
# =========================
def test_wishlist_page_status(client):
    response = client.get("/wishlist")
    assert response.status_code == 200

# =========================
# TEST 2: PAGE TITLE EXISTS
# =========================
def test_wishlist_title(client):
    response = client.get("/wishlist")
    html = response.get_data(as_text=True).lower()

    assert "my wishlist" in html
    assert "thrill sphere" in html
