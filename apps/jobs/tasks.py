"""
Celery tasks for jobs app.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import Job, Application
from apps.core.notification_service import NotificationService
from apps.core.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_job_expiration(self):
    """
    Process job expiration and auto-close expired jobs.
    """
    try:
        now = timezone.now()
        expired_jobs = Job.objects.filter(
            status='active',
            expires_at__lte=now
        )
        
        closed_count = 0
        renewed_count = 0
        
        for job in expired_jobs:
            try:
                if job.auto_renew:
                    # Renew the job
                    renewal_days = 30  # Default renewal period
                    job.expires_at = now + timedelta(days=renewal_days)
                    job.renewal_count += 1
                    job.save(update_fields=['expires_at', 'renewal_count'])
                    renewed_count += 1
                    
                    # Notify employer
                    NotificationService.create_notification(
                        user=job.employer,
                        notification_type='job_posted',
                        title='Job Renewed',
                        message=f'Your job "{job.title}" has been automatically renewed.',
                        priority='normal',
                        action_url=f'/api/jobs/{job.id}/',
                        related_object_type='job',
                        related_object_id=job.id
                    )
                else:
                    # Close the job
                    job.status = 'closed'
                    job.save(update_fields=['status'])
                    closed_count += 1
                    
                    # Notify employer
                    NotificationService.create_notification(
                        user=job.employer,
                        notification_type='system',
                        title='Job Expired',
                        message=f'Your job "{job.title}" has expired and been closed.',
                        priority='normal',
                        action_url=f'/api/jobs/{job.id}/',
                        related_object_type='job',
                        related_object_id=job.id
                    )
            except Exception as e:
                logger.error(f"Error processing job {job.id}: {e}")
        
        logger.info(f"Processed {expired_jobs.count()} expired jobs. Closed: {closed_count}, Renewed: {renewed_count}")
        return {
            'processed': expired_jobs.count(),
            'closed': closed_count,
            'renewed': renewed_count
        }
    except Exception as e:
        logger.error(f"Error in process_job_expiration task: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_scheduled_jobs(self):
    """
    Publish scheduled jobs that are ready to be published.
    """
    try:
        now = timezone.now()
        scheduled_jobs = Job.objects.filter(
            status='draft',
            scheduled_publish_date__lte=now,
            approval_status='approved'
        )
        
        published_count = 0
        
        for job in scheduled_jobs:
            try:
                job.status = 'active'
                job.scheduled_publish_date = None
                job.save(update_fields=['status', 'scheduled_publish_date'])
                published_count += 1
                
                # Notify employer
                NotificationService.create_notification(
                    user=job.employer,
                    notification_type='job_posted',
                    title='Job Published',
                    message=f'Your scheduled job "{job.title}" has been published.',
                    priority='normal',
                    action_url=f'/api/jobs/{job.id}/',
                    related_object_type='job',
                    related_object_id=job.id
                )
            except Exception as e:
                logger.error(f"Error publishing job {job.id}: {e}")
        
        logger.info(f"Published {published_count} scheduled jobs")
        return {'published': published_count}
    except Exception as e:
        logger.error(f"Error in process_scheduled_jobs task: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_application_deadline_reminders(self):
    """
    Send reminders for applications approaching deadline.
    """
    try:
        tomorrow = timezone.now().date() + timedelta(days=1)
        jobs_ending_soon = Job.objects.filter(
            status='active',
            application_deadline=tomorrow
        )
        
        reminder_count = 0
        
        for job in jobs_ending_soon:
            try:
                # Notify employer
                NotificationService.create_notification(
                    user=job.employer,
                    notification_type='application_deadline',
                    title='Application Deadline Tomorrow',
                    message=f'Applications for "{job.title}" close tomorrow.',
                    priority='high',
                    action_url=f'/api/jobs/{job.id}/',
                    related_object_type='job',
                    related_object_id=job.id
                )
                reminder_count += 1
            except Exception as e:
                logger.error(f"Error sending reminder for job {job.id}: {e}")
        
        logger.info(f"Sent {reminder_count} application deadline reminders")
        return {'reminders_sent': reminder_count}
    except Exception as e:
        logger.error(f"Error in send_application_deadline_reminders task: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_email_async(self, email_type, **kwargs):
    """
    Send email asynchronously.
    
    Args:
        email_type: Type of email to send
        **kwargs: Email parameters
    """
    try:
        if email_type == 'application_confirmation':
            EmailService.send_application_confirmation(kwargs['application'])
        elif email_type == 'new_application_notification':
            EmailService.send_new_application_notification(kwargs['application'])
        elif email_type == 'application_status_update':
            EmailService.send_application_status_update(
                kwargs['application'],
                kwargs.get('old_status')
            )
        elif email_type == 'job_posted_confirmation':
            EmailService.send_job_posted_confirmation(kwargs['job'])
        elif email_type == 'job_status_change':
            EmailService.send_job_status_change_notification(
                kwargs['job'],
                kwargs.get('old_status')
            )
        else:
            logger.warning(f"Unknown email type: {email_type}")
        
        return {'status': 'sent', 'email_type': email_type}
    except Exception as e:
        logger.error(f"Error sending email {email_type}: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_file_async(self, file_path, process_type, **kwargs):
    """
    Process files asynchronously (resume parsing, image optimization, etc.).
    
    Args:
        file_path: Path to file
        process_type: Type of processing (resume_parse, image_optimize, pdf_thumbnail)
        **kwargs: Processing parameters
    """
    try:
        from apps.core.file_processing import (
            optimize_image, generate_pdf_thumbnail, parse_resume
        )
        
        if process_type == 'resume_parse':
            result = parse_resume(file_path)
        elif process_type == 'image_optimize':
            result = optimize_image(file_path, **kwargs)
        elif process_type == 'pdf_thumbnail':
            result = generate_pdf_thumbnail(file_path, **kwargs)
        else:
            logger.warning(f"Unknown process type: {process_type}")
            return {'status': 'error', 'message': f'Unknown process type: {process_type}'}
        
        return {'status': 'completed', 'process_type': process_type, 'result': result}
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        raise self.retry(exc=e, countdown=60)
