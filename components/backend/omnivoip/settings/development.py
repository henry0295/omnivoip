"""
Development settings for OmniVoIP project.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Development-specific apps (optional)
# INSTALLED_APPS += [
#     'django_extensions',
# ]

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Session cookie security (disabled for dev)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email backend (console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable template caching in development
TEMPLATES[0]['OPTIONS']['debug'] = True

# SQLite for quick local testing (optional)
# Uncomment to use SQLite instead of PostgreSQL in development
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
