from app import create_app
import pytest


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client
# =========================
# NAVIGATION ELEMENTS
# =========================
def test_nav_elements_exist(client):
    response = client.get("/")
    html = response.get_data(as_text=True).lower()

    assert "nav-toggle" in html
    assert "data-nav-content" in html
    assert "data-nav-link" in html

