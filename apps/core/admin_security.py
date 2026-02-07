"""
Admin configuration for security models.
"""
from django.contrib import admin
from apps.core.models_security import APIKey, IPWhitelist, SecurityEvent


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin interface for APIKey model."""
    list_display = ('name', 'user', 'is_active', 'last_used_at', 'expires_at', 'created_at')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('key', 'last_used_at', 'created_at', 'updated_at')
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('Key Information', {
            'fields': ('name', 'key', 'user', 'is_active')
        }),
        ('Usage', {
            'fields': ('last_used_at', 'expires_at', 'rate_limit')
        }),
        ('Security', {
            'fields': ('allowed_ips', 'scopes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(IPWhitelist)
class IPWhitelistAdmin(admin.ModelAdmin):
    """Admin interface for IPWhitelist model."""
    list_display = ('ip_address', 'description', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('ip_address', 'description')
    raw_id_fields = ('created_by',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """Admin interface for SecurityEvent model."""
    list_display = ('event_type', 'user', 'ip_address', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_type', 'user', 'ip_address', 'user_agent')
        }),
        ('Details', {
            'fields': ('details',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
