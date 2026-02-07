"""
Django signals for core app.

Currently, core app models (AuditLog, Notification, etc.) are handled through
services rather than signals. This file is kept for future signal handlers
if needed.
"""
import logging

logger = logging.getLogger(__name__)

# Signal handlers for core app models can be added here if needed in the future
# Example:
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from .models_audit import AuditLog
# from .models_notifications import Notification
#
# @receiver(post_save, sender=AuditLog)
# def audit_log_post_save_handler(sender, instance, created, **kwargs):
#     """Handle audit log creation."""
#     pass
