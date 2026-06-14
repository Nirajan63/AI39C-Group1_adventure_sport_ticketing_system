import os
from dotenv import load_dotenv

# Load values from .env file (ignored if file not present)
load_dotenv()

# ─────────────────────────────────────────────
#  Database Configuration
# ─────────────────────────────────────────────
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///dev.db')

# ─────────────────────────────────────────────
#  Application Secret Key
#  Loaded from .env — never hardcode in source
# ─────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'fallback-insecure-key-replace-in-production'
)
