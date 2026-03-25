import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/medkids")

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

# Email Configuration (Gmail SMTP)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")  # Your Gmail email
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Your Gmail app password

# App Settings
APP_NAME = "MEDKids OrderUp"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")
DEBUG = os.getenv("DEBUG", "True") == "True"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")