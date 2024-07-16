import os
from pathlib import Path

import backoff
from dotenv import load_dotenv
from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DEBUG", "False") == "True"

if DEBUG:
    load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")


AUTH_API_LOGIN_URL = os.environ.get("AUTH_API_LOGIN_URL")
AUTH_API_PROFILE_URL = os.environ.get("AUTH_API_PROFILE_URL")

BACKOFF_MAX_RETRIES = os.environ.get("BACKOFF_MAX_RETRIES") or 6

ALLOWED_HOSTS = (
    os.environ.get("ALLOWED_HOSTS").split(",")
    if os.environ.get("ALLOWED_HOSTS")
    else ["127.0.0.1", "localhost"]
)

CSRF_TRUSTED_ORIGINS = (
    os.environ.get("CSRF_TRUSTED_ORIGINS").split(",")
    if os.environ.get("CSRF_TRUSTED_ORIGINS")
    else [
        "http://127.0.0.1",
        "https://127.0.0.1",
        "http://localhost",
        "https://localhost",
    ]
)


INTERNAL_IPS = (
    os.environ.get("INTERNAL_HOSTS").split(",")
    if os.environ.get("INTERNAL_HOSTS")
    else ["127.0.0.1"]
)


BACKOFF_CONFIG = {
    "wait_gen": backoff.expo,
    "exception": ConnectionError,
    "max_tries": BACKOFF_MAX_RETRIES,
}

CIRCUIT_CONFIG = {"failure_threshold": 5, "expected_exception": ConnectionError}

include(
    "components/*.py",
)
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
