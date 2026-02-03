"""
Email service for sending notifications.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for sending emails with HTML and plain text templates.
    
    Features:
    - HTML and plain text email support
    - Template rendering
    - Error handling and logging
    - Configurable from email
    """
    
    @staticmethod
    def send_email(
        subject,
        template_name,
        context,
        recipient_list,
        from_email=None,
        fail_silently=False
    ):
        """
        Send an email with HTML and plain text versions.
        
        Args:
            subject: Email subject line
            template_name: Base name of template (without .html/.txt)
            context: Dictionary of template variables
            recipient_list: List of recipient email addresses
            from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
            fail_silently: If True, suppress exceptions
        
        Returns:
            Number of emails sent (0 or 1)
        """
        if not recipient_list:
            logger.warning("No recipients provided for email")
            return 0
        
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        
        try:
            # Render HTML template
            html_template = f'emails/{template_name}.html'
            html_message = render_to_string(html_template, context)
            
            # Render plain text template (fallback)
            text_template = f'emails/{template_name}.txt'
            try:
                text_message = render_to_string(text_template, context)
            except Exception:
                # Fallback: strip HTML tags if text template doesn't exist
                text_message = strip_tags(html_message)
            
            # Create email message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=from_email,
                to=recipient_list
            )
            msg.attach_alternative(html_message, "text/html")
            
            # Send email
            result = msg.send(fail_silently=fail_silently)
            
            if result:
                logger.info(f"Email sent successfully to {recipient_list}")
            else:
                logger.warning(f"Failed to send email to {recipient_list}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}", exc_info=True)
            if not fail_silently:
                raise
            return 0
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to newly registered user."""
        context = {
            'user': user,
            'site_name': getattr(settings, 'SITE_NAME', 'Job Board Platform'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        subject = f'Welcome to {context["site_name"]}!'
        return EmailService.send_email(
            subject=subject,
            template_name='welcome',
            context=context,
            recipient_list=[user.email]
        )
    
    @staticmethod
    def send_application_confirmation(application):
        """Send confirmation email to applicant."""
        context = {
            'application': application,
            'job': application.job,
            'applicant': application.applicant,
            'site_name': getattr(settings, 'SITE_NAME', 'Job Board Platform'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        subject = f'Application Submitted: {application.job.title}'
        return EmailService.send_email(
            subject=subject,
            template_name='application_confirmation',
            context=context,
            recipient_list=[application.applicant.email]
        )
    
    @staticmethod
    def send_new_application_notification(application):
        """Send notification to employer about new application."""
        context = {
            'application': application,
            'job': application.job,
            'applicant': application.applicant,
            'employer': application.job.employer,
            'site_name': getattr(settings, 'SITE_NAME', 'Job Board Platform'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        subject = f'New Application for: {application.job.title}'
        return EmailService.send_email(
            subject=subject,
            template_name='new_application_notification',
            context=context,
            recipient_list=[application.job.employer.email]
        )
    
    @staticmethod
    def send_application_status_update(application, old_status=None):
        """Send email when application status changes."""
        context = {
            'application': application,
            'job': application.job,
            'applicant': application.applicant,
            'old_status': old_status,
            'new_status': application.status,
            'site_name': getattr(settings, 'SITE_NAME', 'Job Board Platform'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        
        # Different subject based on status
        status_subjects = {
            'accepted': f'Congratulations! Your application for {application.job.title}',
            'rejected': f'Update on your application for {application.job.title}',
            'reviewed': f'Your application for {application.job.title} is under review',
        }
        subject = status_subjects.get(
            application.status,
            f'Application Status Update: {application.job.title}'
        )
        
        return EmailService.send_email(
            subject=subject,
            template_name='application_status_update',
            context=context,
            recipient_list=[application.applicant.email]
        )
    
    @staticmethod
    def send_job_posted_confirmation(job):
        """Send confirmation email to employer when job is posted."""
        context = {
            'job': job,
            'employer': job.employer,
            'site_name': getattr(settings, 'SITE_NAME', 'Job Board Platform'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        subject = f'Job Posted Successfully: {job.title}'
        return EmailService.send_email(
            subject=subject,
            template_name='job_posted_confirmation',
            context=context,
            recipient_list=[job.employer.email]
        )
    
    @staticmethod
    def send_job_status_change_notification(job, old_status):
        """Send notification when job status changes."""
        context = {
            'job': job,
            'employer': job.employer,
            'old_status': old_status,
            'new_status': job.status,
            'site_name': getattr(settings, 'SITE_NAME', 'Job Board Platform'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        subject = f'Job Status Updated: {job.title}'
        return EmailService.send_email(
            subject=subject,
            template_name='job_status_change',
            context=context,
            recipient_list=[job.employer.email]
        )
    
    @staticmethod
    def send_application_deadline_reminder(job):
        """Send reminder email about approaching application deadline."""
        context = {
            'job': job,
            'employer': job.employer,
            'days_remaining': job.days_until_deadline,
            'site_name': getattr(settings, 'SITE_NAME', 'Job Board Platform'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        subject = f'Application Deadline Reminder: {job.title}'
        return EmailService.send_email(
            subject=subject,
            template_name='deadline_reminder',
            context=context,
            recipient_list=[job.employer.email]
        )
