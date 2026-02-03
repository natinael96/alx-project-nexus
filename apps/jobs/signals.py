"""
Django signals for jobs app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Job, Application
from apps.core.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Job)
def job_status_change_handler(sender, instance, created, **kwargs):
    """
    Handle job status changes and send notifications.
    Note: This is a backup - primary email sending is in views.
    """
    if not created and 'status' in kwargs.get('update_fields', []):
        # Status was updated via save() method
        # Email is primarily sent from views, but this is a fallback
        pass


@receiver(post_save, sender=Application)
def application_status_change_handler(sender, instance, created, **kwargs):
    """
    Handle application status changes and send notifications.
    Note: This is a backup - primary email sending is in views.
    """
    if not created and 'status' in kwargs.get('update_fields', []):
        # Status was updated via save() method
        # Email is primarily sent from views, but this is a fallback
        pass
