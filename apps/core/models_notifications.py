"""
Notification models for in-app notifications.
"""
from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class Notification(models.Model):
    """
    Model for in-app notifications.
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('job_application', 'Job Application'),
        ('application_status', 'Application Status Update'),
        ('job_posted', 'Job Posted'),
        ('job_expiring', 'Job Expiring Soon'),
        ('application_deadline', 'Application Deadline Reminder'),
        ('new_job_match', 'New Job Match'),
        ('message', 'Message'),
        ('system', 'System Notification'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='User who receives this notification'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        db_index=True,
        help_text='Type of notification'
    )
    title = models.CharField(
        max_length=200,
        help_text='Notification title'
    )
    message = models.TextField(
        help_text='Notification message'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        db_index=True,
        help_text='Notification priority'
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Whether notification has been read'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When notification was read'
    )
    action_url = models.URLField(
        blank=True,
        help_text='URL to navigate to when notification is clicked'
    )
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Type of related object (e.g., job, application)'
    )
    related_object_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID of related object'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional notification metadata'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', 'notification_type', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread."""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])


class NotificationPreference(models.Model):
    """
    Model for user notification preferences (extends UserPreferences).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        help_text='User notification preferences'
    )
    
    # In-app notification preferences
    in_app_job_applications = models.BooleanField(
        default=True,
        help_text='Receive in-app notifications for job applications'
    )
    in_app_application_updates = models.BooleanField(
        default=True,
        help_text='Receive in-app notifications for application status updates'
    )
    in_app_new_jobs = models.BooleanField(
        default=True,
        help_text='Receive in-app notifications for new matching jobs'
    )
    in_app_messages = models.BooleanField(
        default=True,
        help_text='Receive in-app notifications for messages'
    )
    in_app_system = models.BooleanField(
        default=True,
        help_text='Receive in-app system notifications'
    )
    
    # Notification frequency
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
        ],
        default='immediate',
        help_text='Notification frequency preference'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
