"""
Notification service for creating and managing notifications.
"""
import logging
from typing import Optional, Dict, List
from django.utils import timezone
from apps.core.models_notifications import Notification, NotificationPreference
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for creating and managing notifications.
    """
    
    @staticmethod
    def create_notification(
        user: User,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'normal',
        action_url: Optional[str] = None,
        related_object_type: Optional[str] = None,
        related_object_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Notification:
        """
        Create a notification for a user.
        
        Args:
            user: User to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Notification priority (low, normal, high, urgent)
            action_url: URL to navigate to when clicked
            related_object_type: Type of related object
            related_object_id: ID of related object
            metadata: Additional metadata
            
        Returns:
            Created Notification instance
        """
        # Check user's notification preferences
        try:
            prefs = NotificationPreference.objects.get(user=user)
            
            # Check if user wants this type of notification
            if not NotificationService._should_send_notification(prefs, notification_type):
                logger.debug(f"User {user.id} has disabled {notification_type} notifications")
                return None
        except NotificationPreference.DoesNotExist:
            # Default to sending if preferences don't exist
            pass
        
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                action_url=action_url or '',
                related_object_type=related_object_type or '',
                related_object_id=related_object_id,
                metadata=metadata or {}
            )
            
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def _should_send_notification(prefs: NotificationPreference, notification_type: str) -> bool:
        """Check if notification should be sent based on preferences."""
        type_mapping = {
            'job_application': prefs.in_app_job_applications,
            'application_status': prefs.in_app_application_updates,
            'job_posted': prefs.in_app_new_jobs,
            'new_job_match': prefs.in_app_new_jobs,
            'message': prefs.in_app_messages,
            'system': prefs.in_app_system,
        }
        return type_mapping.get(notification_type, True)
    
    @staticmethod
    def mark_as_read(notification_id: int, user: User) -> bool:
        """Mark a notification as read."""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user: User) -> int:
        """Mark all notifications as read for a user."""
        count = Notification.objects.filter(
            user=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        return count
    
    @staticmethod
    def get_unread_count(user: User) -> int:
        """Get count of unread notifications for a user."""
        return Notification.objects.filter(user=user, is_read=False).count()
    
    @staticmethod
    def delete_old_notifications(days: int = 90) -> int:
        """Delete notifications older than specified days."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        count, _ = Notification.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        return count
