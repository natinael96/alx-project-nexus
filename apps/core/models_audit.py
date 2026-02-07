"""
Audit logging models for tracking all system changes.
"""
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.accounts.models import User


class AuditLog(models.Model):
    """
    Model for audit logging - tracks all create, update, delete operations.
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('permission_change', 'Permission Change'),
        ('status_change', 'Status Change'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text='User who performed the action (null for system actions)'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text='Action performed'
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Type of object affected'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='ID of object affected'
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    object_repr = models.CharField(
        max_length=255,
        help_text='String representation of the object'
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text='Changes made (field: {old: value, new: value})'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the user'
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text='User agent string'
    )
    request_path = models.CharField(
        max_length=500,
        blank=True,
        help_text='API endpoint or URL path'
    )
    request_method = models.CharField(
        max_length=10,
        blank=True,
        help_text='HTTP method (GET, POST, etc.)'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str}: {self.action} on {self.object_repr}"


class ChangeHistory(models.Model):
    """
    Model for tracking detailed change history of specific objects.
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text='Type of object'
    )
    object_id = models.PositiveIntegerField(
        help_text='ID of object'
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_history',
        help_text='User who made the change'
    )
    field_name = models.CharField(
        max_length=100,
        help_text='Name of the field that changed'
    )
    old_value = models.TextField(
        blank=True,
        help_text='Old value (serialized)'
    )
    new_value = models.TextField(
        blank=True,
        help_text='New value (serialized)'
    )
    change_reason = models.TextField(
        blank=True,
        help_text='Reason for the change'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'change_history'
        verbose_name = 'Change History'
        verbose_name_plural = 'Change Histories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-created_at']),
            models.Index(fields=['changed_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.field_name} changed on {self.content_type.model} #{self.object_id}"
