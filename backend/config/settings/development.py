"""
Development settings — SQLite for local dev (no Postgres needed),
local media, debug mode.
"""
from .base import *  # noqa: F401, F403
from decouple import config

DEBUG = True

# Use SQLite locally so no Postgres install is required.
# Set USE_POSTGRES=True (or supply DB_* env vars) to switch to Postgres.
if config("USE_POSTGRES", default=False, cast=bool):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME", default="garbagems"),
            "USER": config("DB_USER", default="dev"),
            "PASSWORD": config("DB_PASSWORD", default="dev"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Local media storage
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Email to console for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Relax password validation in dev
AUTH_PASSWORD_VALIDATORS = []
