"""
Admin configuration for core app.
"""
from django.contrib import admin

# Import notification admin
from . import admin_notifications  # noqa

# Import audit admin
from . import admin_audit  # noqa
