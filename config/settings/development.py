"""
Development settings.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

SECRET_KEY = "django-insecure-dev-only-key-not-for-production"

# Email — log to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
