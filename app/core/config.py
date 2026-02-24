import os

ENV = os.getenv("ENV", "local")

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# Optional SQL logging
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"
