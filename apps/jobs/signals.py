"""
Django signals for jobs app.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.core.email_service import EmailService
from apps.core.cache_utils import invalidate_category_cache, invalidate_job_cache
from .models import Job, Application, Category

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Job)
def job_post_save_handler(sender, instance, created, **kwargs):
    """
    Handles post-save events for Job model to send email notifications and invalidate cache.
    """
    # Invalidate cache
    try:
        invalidate_job_cache(instance.id if not created else None)
    except Exception as e:
        logger.error(f"Failed to invalidate job cache for Job ID {instance.id}: {e}")
    
    # Email notifications are handled in views, but this is a fallback
    if created:
        # Send job posted confirmation to employer
        try:
            EmailService.send_job_posted_confirmation(instance)
        except Exception as e:
            logger.error(f"Failed to send job posted confirmation for Job ID {instance.id}: {e}")
    else:
        # Check if status has changed to send notification
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                EmailService.send_job_status_change_notification(instance, old_instance.status)
        except sender.DoesNotExist:
            logger.warning(f"Job instance with ID {instance.id} not found for status change check.")
        except Exception as e:
            logger.error(f"Failed to send job status change notification for Job ID {instance.id}: {e}")


@receiver(post_delete, sender=Job)
def job_post_delete_handler(sender, instance, **kwargs):
    """
    Handle post-delete events for Job model to invalidate cache.
    """
    try:
        invalidate_job_cache(instance.id)
    except Exception as e:
        logger.error(f"Failed to invalidate job cache after deletion: {e}")


@receiver(post_save, sender=Application)
def application_post_save_handler(sender, instance, created, **kwargs):
    """
    Handles post-save events for Application model to send email notifications.
    """
    if not instance.applicant or not instance.job or not instance.job.employer:
        logger.warning(f"Skipping application email for ID {instance.id} due to missing related data.")
        return

    if created:
        # Send application confirmation to applicant
        try:
            EmailService.send_application_confirmation(instance)
        except Exception as e:
            logger.error(f"Failed to send application confirmation for Application ID {instance.id}: {e}")

        # Send new application notification to employer
        try:
            EmailService.send_new_application_notification(instance)
        except Exception as e:
            logger.error(f"Failed to send new application notification for Application ID {instance.id}: {e}")
    else:
        # Check if status has changed to send notification
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                EmailService.send_application_status_update(instance, old_instance.status)
        except sender.DoesNotExist:
            logger.warning(f"Application instance with ID {instance.id} not found for status change check.")
        except Exception as e:
            logger.error(f"Failed to send application status update for Application ID {instance.id}: {e}")


@receiver(post_save, sender=Category)
def category_post_save_handler(sender, instance, created, **kwargs):
    """
    Handle post-save events for Category model to invalidate cache.
    """
    try:
        invalidate_category_cache(instance.id if not created else None)
    except Exception as e:
        logger.error(f"Failed to invalidate category cache for Category ID {instance.id}: {e}")


@receiver(post_delete, sender=Category)
def category_post_delete_handler(sender, instance, **kwargs):
    """
    Handle post-delete events for Category model to invalidate cache.
    """
    try:
        invalidate_category_cache(instance.id)
    except Exception as e:
        logger.error(f"Failed to invalidate category cache after deletion: {e}")
