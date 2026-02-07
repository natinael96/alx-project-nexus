"""
Serializers for notification models.
"""
from rest_framework import serializers
from apps.core.models_notifications import Notification, NotificationPreference
from apps.accounts.models import User


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = (
            'id', 'notification_type', 'notification_type_display',
            'title', 'message', 'priority', 'priority_display',
            'is_read', 'read_at', 'action_url',
            'related_object_type', 'related_object_id',
            'metadata', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'read_at')


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationPreference model.
    """
    notification_frequency_display = serializers.CharField(source='get_notification_frequency_display', read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = (
            'in_app_job_applications', 'in_app_application_updates',
            'in_app_new_jobs', 'in_app_messages', 'in_app_system',
            'notification_frequency', 'notification_frequency_display',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
