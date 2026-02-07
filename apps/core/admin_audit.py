"""
Admin configuration for audit logging models.
"""
from django.contrib import admin
from .models_audit import AuditLog, ChangeHistory


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for AuditLog model.
    """
    list_display = ('user', 'action', 'object_repr', 'ip_address', 'request_method', 'created_at')
    list_filter = ('action', 'request_method', 'created_at')
    search_fields = ('user__username', 'user__email', 'object_repr', 'request_path', 'ip_address')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Action Details', {
            'fields': ('user', 'action', 'content_type', 'object_id', 'object_repr')
        }),
        ('Changes', {
            'fields': ('changes',),
            'classes': ('collapse',)
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent', 'request_path', 'request_method')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user', 'content_type')


@admin.register(ChangeHistory)
class ChangeHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for ChangeHistory model.
    """
    list_display = ('content_type', 'object_id', 'field_name', 'changed_by', 'created_at')
    list_filter = ('content_type', 'field_name', 'created_at')
    search_fields = ('field_name', 'old_value', 'new_value', 'changed_by__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('changed_by', 'content_type')
