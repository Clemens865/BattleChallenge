"""Application configuration."""

# Database settings
DATABASE_URL = "sqlite:///auth.db"
DATABASE_ECHO = False

# Authentication settings
HASH_ALGORITHM = "md5"
SESSION_EXPIRY_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# Password policy
MIN_PASSWORD_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_DIGIT = True

# Application settings
APP_NAME = "AuthSystem"
APP_VERSION = "1.0.0"
DEBUG = False
