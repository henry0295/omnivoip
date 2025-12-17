"""
WSGI config for OmniVoIP project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omnivoip.settings.production')

application = get_wsgi_application()
