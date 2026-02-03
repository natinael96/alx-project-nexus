"""
Settings module initialization.
Determines which settings to import based on environment variable.
"""
import os

# Determine which settings to import based on environment
ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development').strip().lower()

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    from .development import *

