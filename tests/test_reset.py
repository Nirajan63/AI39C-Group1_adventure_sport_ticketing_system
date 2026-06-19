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