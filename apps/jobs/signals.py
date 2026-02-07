"""
Django signals for jobs app.
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from apps.core.email_service import EmailService
from apps.core.cache_utils import invalidate_category_cache, invalidate_job_cache

# Import async email task (with fallback if Celery not available)
try:
    from apps.jobs.tasks import send_email_async
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    send_email_async = None
from apps.core.file_management import cleanup_application_files
from .models import Job, Application, Category
from django.conf import settings

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
        # Send job posted confirmation to employer (async if available)
        try:
            if CELERY_AVAILABLE and send_email_async:
                send_email_async.delay('job_posted_confirmation', job=instance)
            else:
                EmailService.send_job_posted_confirmation(instance)
        except Exception as e:
            logger.error(f"Failed to send job posted confirmation for Job ID {instance.id}: {e}")
    else:
        # Check if status has changed to send notification
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Send notification async if available
                try:
                    if CELERY_AVAILABLE and send_email_async:
                        send_email_async.delay('job_status_change', job=instance, old_status=old_instance.status)
                    else:
                        EmailService.send_job_status_change_notification(instance, old_instance.status)
                except Exception as e:
                    logger.error(f"Failed to send job status change notification for Job ID {instance.id}: {e}")
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
    Handles post-save events for Application model to send email notifications and track status history.
    """
    if not instance.applicant or not instance.job or not instance.job.employer:
        logger.warning(f"Skipping application email for ID {instance.id} due to missing related data.")
        return

    if created:
        # Send application confirmation to applicant (async if available)
        try:
            if CELERY_AVAILABLE and send_email_async:
                send_email_async.delay('application_confirmation', application=instance)
            else:
                EmailService.send_application_confirmation(instance)
        except Exception as e:
            logger.error(f"Failed to send application confirmation for Application ID {instance.id}: {e}")

        # Send new application notification to employer (async if available)
        try:
            if CELERY_AVAILABLE and send_email_async:
                send_email_async.delay('new_application_notification', application=instance)
            else:
                EmailService.send_new_application_notification(instance)
        except Exception as e:
            logger.error(f"Failed to send new application notification for Application ID {instance.id}: {e}")
        
        # Create in-app notification for employer
        try:
            from apps.core.notification_service import NotificationService
            NotificationService.create_notification(
                user=instance.job.employer,
                notification_type='job_application',
                title='New Application',
                message=f'New application received for "{instance.job.title}"',
                priority='high',
                action_url=f'/api/applications/{instance.id}/',
                related_object_type='application',
                related_object_id=instance.id
            )
        except Exception as e:
            logger.error(f"Failed to create notification for Application ID {instance.id}: {e}")
        
        # Create initial status history
        try:
            from apps.jobs.models_application_enhancements import ApplicationStatusHistory
            ApplicationStatusHistory.objects.create(
                application=instance,
                old_status=None,
                new_status=instance.status,
                changed_by=None,  # System
                reason='Application submitted'
            )
        except Exception as e:
            logger.error(f"Failed to create status history for Application ID {instance.id}: {e}")
    else:
        # Check if status has changed to send notification and track history
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Send email notification async if available
                try:
                    if CELERY_AVAILABLE and send_email_async:
                        send_email_async.delay('application_status_update', application=instance, old_status=old_instance.status)
                    else:
                        EmailService.send_application_status_update(instance, old_instance.status)
                except Exception as e:
                    logger.error(f"Failed to send application status update for Application ID {instance.id}: {e}")
                
                # Create in-app notification for applicant
                try:
                    from apps.core.notification_service import NotificationService
                    status_display = dict(Application.STATUS_CHOICES).get(instance.status, instance.status)
                    NotificationService.create_notification(
                        user=instance.applicant,
                        notification_type='application_status',
                        title='Application Status Updated',
                        message=f'Your application for "{instance.job.title}" status changed to {status_display}',
                        priority='normal',
                        action_url=f'/api/applications/{instance.id}/',
                        related_object_type='application',
                        related_object_id=instance.id
                    )
                except Exception as e:
                    logger.error(f"Failed to create notification for Application ID {instance.id}: {e}")
                
                # Create status history
                try:
                    from apps.jobs.models_application_enhancements import ApplicationStatusHistory
                    ApplicationStatusHistory.objects.create(
                        application=instance,
                        old_status=old_instance.status,
                        new_status=instance.status,
                        changed_by=getattr(instance, '_status_changed_by', None),  # Set in view
                        reason=getattr(instance, '_status_change_reason', '')
                    )
                except Exception as e:
                    logger.error(f"Failed to create status history for Application ID {instance.id}: {e}")
        except sender.DoesNotExist:
            logger.warning(f"Application instance with ID {instance.id} not found for status change check.")
        except Exception as e:
            logger.error(f"Failed to process application status update for Application ID {instance.id}: {e}")


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


@receiver(pre_delete, sender=Application)
def application_pre_delete_handler(sender, instance, **kwargs):
    """
    Handle pre-delete events for Application model to clean up files.
    """
    try:
        cleanup_application_files(instance)
    except Exception as e:
        logger.error(f"Failed to clean up application files: {e}")
