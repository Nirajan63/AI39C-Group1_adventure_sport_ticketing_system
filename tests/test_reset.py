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


# ==================================================
# TEST 7: RESET FAILS WHEN NO OTP WAS EVER REQUESTED
# ==================================================
def test_reset_without_requesting_otp(client, db_user):
    response = client.post(
        "/forgot",
        json={
            "action": "reset",
            "email": db_user["email"],
            "code": "000000",
            "password": "WhateverPass123",
        },
    )
    data = response.get_json()

    assert response.status_code == 400
    assert "no code" in data["message"].lower()


# ==================================================
# TEST 8: RESET FAILS WITH AN INCORRECT OTP CODE
# ==================================================
def test_reset_with_wrong_otp(client, db_user):
    send_resp = client.post(
        "/forgot", json={"action": "send_otp", "email": db_user["email"]}
    )
    assert send_resp.status_code == 200

    real_otp = read_mock_otp()
    wrong_otp = "111111" if real_otp != "111111" else "222222"

    reset_resp = client.post(
        "/forgot",
        json={
            "action": "reset",
            "email": db_user["email"],
            "code": wrong_otp,
            "password": "NewPassword123",
        },
    )
    data = reset_resp.get_json()

    assert reset_resp.status_code == 400
    assert data["status"] == "error"

    # Password in the DB must be untouched
    assert get_db_password(db_user["email"]) == db_user["password"]


# ==========================================================
# TEST 9: FULL HAPPY-PATH FLOW — REQUEST OTP -> RESET -> DB CHECK
# ==========================================================
def test_full_reset_password_flow(client, db_user):
    # Step 1: request OTP
    send_resp = client.post(
        "/forgot", json={"action": "send_otp", "email": db_user["email"]}
    )
    assert send_resp.status_code == 200
    assert send_resp.get_json()["status"] == "success"

    # Step 2: grab the OTP the backend wrote to app/mock_otp.txt
    otp_code = read_mock_otp()
    assert len(otp_code) == 6 and otp_code.isdigit()

    # Step 3: submit the OTP + new password
    new_password = "BrandNewPass456"
    reset_resp = client.post(
        "/forgot",
        json={
            "action": "reset",
            "email": db_user["email"],
            "code": otp_code,
            "password": new_password,
        },
    )
    reset_data = reset_resp.get_json()
    assert reset_resp.status_code == 200
    assert reset_data["status"] == "success"

    # Step 4: verify directly in the DB (no /login route involved)
    assert get_db_password(db_user["email"]) == new_password


# ==========================================================
# TEST 10: OTP CANNOT BE REUSED AFTER A SUCCESSFUL RESET
# ==========================================================
def test_otp_cannot_be_reused(client, db_user):
    client.post("/forgot", json={"action": "send_otp", "email": db_user["email"]})
    otp_code = read_mock_otp()

    first_reset = client.post(
        "/forgot",
        json={
            "action": "reset",
            "email": db_user["email"],
            "code": otp_code,
            "password": "FirstNewPass789",
        },
    )
    assert first_reset.status_code == 200

    # Re-using the same OTP a second time must fail (it was popped from the store)
    second_reset = client.post(
        "/forgot",
        json={
            "action": "reset",
            "email": db_user["email"],
            "code": otp_code,
            "password": "SecondNewPass789",
        },
    )
    data = second_reset.get_json()
    assert second_reset.status_code == 400
    assert data["status"] == "error"

    # Confirm the first reset is the one that stuck
    assert get_db_password(db_user["email"]) == "FirstNewPass789"