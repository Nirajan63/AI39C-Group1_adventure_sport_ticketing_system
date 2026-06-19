"""
Reset Password Test Suite
"""

import os
import uuid
import pytest

from app import create_app
from app.models.database import get_db_connection


# =========================
# FIXTURE (REUSABLE APP)
# =========================
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# Path to app/mock_otp.txt (tests/ is a sibling of app/)
MOCK_OTP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app",
    "mock_otp.txt",
)


def read_mock_otp():
    """Read the most recently generated OTP code written by the app."""
    with open(MOCK_OTP_PATH, "r") as f:
        return f.read().strip()

import os
import uuid
import pytest

from app import create_app
from app.models.database import get_db_connection


# =========================
# FIXTURE (REUSABLE APP)
# =========================
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# Path to app/mock_otp.txt (tests/ is a sibling of app/)
MOCK_OTP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app",
    "mock_otp.txt",
)


def read_mock_otp():
    """Read the most recently generated OTP code written by the app."""
    with open(MOCK_OTP_PATH, "r") as f:
        return f.read().strip()
    
# =========================
# TEST 1: RESET PAGE LOADS
# =========================
def test_forgot_page_status(client):
    response = client.get("/forgot")
    assert response.status_code == 200


# =========================
# TEST 2: RESET PAGE HAS EXPECTED FORM ELEMENTS
# =========================
def test_forgot_page_form_fields(client):
    response = client.get("/forgot")
    html = response.data.lower()

    assert b"forgot password" in html
    assert b"reset-email" in html
    assert b"reset-otp" in html
    assert b"new-password" in html
    assert b"confirm-password" in html


# ==========================================
# TEST 3: SEND OTP FAILS WITHOUT AN EMAIL
# ==========================================
def test_send_otp_missing_email(client):
    response = client.post("/forgot", json={"action": "send_otp", "email": ""})
    data = response.get_json()

    assert response.status_code == 400
    assert data["status"] == "error"


# ==================================================
# TEST 4: SEND OTP FAILS FOR AN UNREGISTERED EMAIL
# ==================================================
def test_send_otp_unregistered_email(client):
    response = client.post(
        "/forgot",
        json={"action": "send_otp", "email": "definitely_not_a_user@example.com"},
    )
    data = response.get_json()

    assert response.status_code == 404
    assert data["status"] == "error"


# ==================================================
# TEST 5: SEND OTP SUCCEEDS FOR A REGISTERED EMAIL
# ==================================================
def test_send_otp_success(client, db_user):
    response = client.post(
        "/forgot", json={"action": "send_otp", "email": db_user["email"]}
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "success"

    otp_code = read_mock_otp()
    assert len(otp_code) == 6 and otp_code.isdigit()


# ==================================================
# TEST 6: RESET FAILS WHEN REQUIRED FIELDS ARE MISSING
# ==================================================
def test_reset_missing_fields(client, db_user):
    response = client.post(
        "/forgot",
        json={"action": "reset", "email": db_user["email"]},
        # no "code" / no "password" supplied
    )
    data = response.get_json()

    assert response.status_code == 400
    assert data["status"] == "error"