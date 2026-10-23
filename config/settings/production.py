"""
Production settings.
"""

import os

import dj_database_url

from .base import *  # noqa: F401, F403

DEBUG = False

# --- SECRET_KEY: required in production, no fallback ---
_SECRET = os.environ.get("DJANGO_SECRET_KEY")
if not _SECRET:
    raise RuntimeError(
        "DJANGO_SECRET_KEY environment variable is required in production. "
        "Generate one with: python -c \"from django.core.management.utils "
        "import get_random_secret_key; print(get_random_secret_key())\""
    )
SECRET_KEY = _SECRET

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host]

# --- DATABASE_URL: required in production, no silent SQLite fallback ---
_DB_URL = os.environ.get("DATABASE_URL")
if not _DB_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is required in production. "
        "Example: postgresql://user:password@host:5432/dbname"
    )

DATABASES = {
    "default": dj_database_url.parse(
        _DB_URL,
        conn_max_age=600,
    )
}

# Explicit order: WhiteNoise right after SecurityMiddleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.RateLimitMiddleware",
]

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# --- Security headers ---
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True").lower() == "true"
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Must be False for HTMX to read CSRF token

SECURE_CONTENT_TYPE_NOSNIFF = True

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@foodbase.by")
