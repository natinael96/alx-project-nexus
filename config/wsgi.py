"""
WSGI config for Job Board Platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use environment variable for settings module, fallback to auto-detection in __init__.py
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'config.settings'
)

application = get_wsgi_application()
