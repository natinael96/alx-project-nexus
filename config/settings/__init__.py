"""
Settings module initialization.
Determines which settings to import based on environment variable.

For Heroku, set the config var:
  heroku config:set DJANGO_ENVIRONMENT=production
"""
import os

# Determine which settings to import based on environment
# On Heroku, set DJANGO_ENVIRONMENT=production via heroku config:set
# The DYNO env var is also auto-set by Heroku, so we can detect it
ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', '').strip().lower()

# Auto-detect Heroku if DJANGO_ENVIRONMENT is not explicitly set
if not ENVIRONMENT and 'DYNO' in os.environ:
    ENVIRONMENT = 'production'
elif not ENVIRONMENT:
    ENVIRONMENT = 'development'

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    from .development import *
