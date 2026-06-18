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

# =========================
# TEST 3: EMPTY STATE EXISTS
# =========================
def test_empty_state_present(client):
    response = client.get("/wishlist")
    html = response.get_data(as_text=True).lower()

    assert "your wishlist is empty" in html
    assert "explore challenges" in html
# =========================
# TEST 4: WISHLIST LOOP SECTION
# =========================
def test_wishlist_loop_section(client):
    response = client.get("/wishlist")
    html = response.get_data(as_text=True).lower()

    # checks Jinja loop output area exists
    assert "activity-card" in html
    assert "wishlist-card-item" in html
# =========================
# =========================
# TEST 5: BOOK NOW LINK EXISTS
# =========================
def test_book_now_link(client):
    response = client.get("/wishlist")
    html = response.get_data(as_text=True).lower()

    assert "book now" in html
    assert "/dashboard" in html
# =========================
# TEST 7: JAVASCRIPT FUNCTION EXISTS
# =========================
def test_js_remove_function(client):
    response = client.get("/wishlist")
    html = response.get_data(as_text=True).lower()

    assert "removewishlistcard" in html
    assert "fetch" in html


