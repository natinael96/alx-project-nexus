"""
Django signals for accounts app.
"""
import logging
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import User
from apps.core.file_management import cleanup_user_files

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=User)
def user_pre_delete_handler(sender, instance, **kwargs):
    """
    Handle pre-delete events for User model to clean up files.
    """
    try:
        cleanup_user_files(instance)
    except Exception as e:
        logger.error(f"Failed to clean up user files: {e}")
