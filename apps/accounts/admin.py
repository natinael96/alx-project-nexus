"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User

# Import profile admin
from . import admin_profile  # noqa


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model.
    
    Security Features:
    - Role-based display and filtering
    - Secure password handling
    - Read-only fields for sensitive data
    """
    list_display = (
        'username', 'email', 'role', 'full_name_display', 
        'is_active', 'date_joined', 'last_login'
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'password_display')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'phone_number', 'profile_picture', 'bio')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'phone_number', 'email', 'first_name', 'last_name')
        }),
    )
    
    def full_name_display(self, obj):
        """Display full name in list view."""
        return obj.get_full_name() or '-'
    full_name_display.short_description = 'Full Name'
    
    def password_display(self, obj):
        """Display password status (read-only for security)."""
        if obj.pk:
            return format_html(
                '<span style="color: green;">✓ Password set</span>'
            )
        return '-'
    password_display.short_description = 'Password'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related()

