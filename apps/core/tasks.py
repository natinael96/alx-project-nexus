"""
Background tasks for core app (synchronous).
"""
from django.utils import timezone
from datetime import timedelta
from apps.core.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


def cleanup_old_notifications(days=90):
    """
    Clean up old notifications.

    Args:
        days: Number of days to keep notifications (default: 90)
    """
    try:
        count = NotificationService.delete_old_notifications(days)
        logger.info(f"Deleted {count} old notifications")
        return {'deleted': count}
    except Exception as e:
        logger.error(f"Error cleaning up notifications: {e}")


def generate_daily_reports():
    """
    Generate daily reports for admins.
    """
    try:
        from apps.jobs.models import Job, Application
        from apps.accounts.models import User

        stats = {
            'date': str(timezone.now().date()),
            'total_jobs': Job.objects.count(),
            'active_jobs': Job.objects.filter(status='active').count(),
            'total_applications': Application.objects.count(),
            'pending_applications': Application.objects.filter(status='pending').count(),
            'total_users': User.objects.count(),
            'new_users_today': User.objects.filter(
                date_joined__date=timezone.now().date()
            ).count(),
        }

        logger.info(f"Generated daily report: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error generating daily reports: {e}")


def send_bulk_notifications(user_ids, notification_type, title, message, **kwargs):
    """
    Send bulk notifications to multiple users.

    Args:
        user_ids: List of user IDs
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        **kwargs: Additional notification parameters
    """
    try:
        from apps.accounts.models import User

        sent_count = 0
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                NotificationService.create_notification(
                    user=user,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    **kwargs
                )
                sent_count += 1
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found")
            except Exception as e:
                logger.error(f"Error sending notification to user {user_id}: {e}")

        logger.info(f"Sent {sent_count} bulk notifications")
        return {'sent': sent_count, 'total': len(user_ids)}
    except Exception as e:
        logger.error(f"Error in send_bulk_notifications: {e}")
