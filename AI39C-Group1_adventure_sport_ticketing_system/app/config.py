import os


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, val = line.split('=', 1)
                
                val = val.strip().strip("'").strip('"')
                os.environ[key.strip()] = val

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sportadventure-secret-key-12345'
    DEBUG = True

    
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME') or ''
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or ''
    SMTP_SENDER = os.environ.get('SMTP_SENDER') or 'SportAdventure Support <no-reply@sportadventure.com>'


