"""
Admin configuration for notification models.
"""
from django.contrib import admin
from .models_notifications import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Notification model.
    """
    list_display = ('user', 'title', 'notification_type', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """
    Admin interface for NotificationPreference model.
    """
    list_display = ('user', 'push_enabled', 'notification_frequency', 'updated_at')
    list_filter = ('push_enabled', 'notification_frequency', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('In-App Notifications', {
            'fields': (
                'in_app_job_applications', 'in_app_application_updates',
                'in_app_new_jobs', 'in_app_messages', 'in_app_system'
            )
        }),
        ('Push Notifications', {
            'fields': (
                'push_enabled', 'push_job_applications', 'push_application_updates',
                'push_new_jobs', 'push_messages'
            )
        }),
        ('Settings', {
            'fields': ('notification_frequency',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')
