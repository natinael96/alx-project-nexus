"""
Admin configuration for user profile models.
"""
from django.contrib import admin
from .models_profile import (
    Skill, Education, WorkHistory, Portfolio,
    SocialLink, UserPreferences, SavedJob
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Admin interface for Skill model.
    """
    list_display = ('user', 'name', 'level', 'years_of_experience', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('user__username', 'user__email', 'name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """
    Admin interface for Education model.
    """
    list_display = ('user', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'institution', 'degree', 'field_of_study')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')


@admin.register(WorkHistory)
class WorkHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for WorkHistory model.
    """
    list_display = ('user', 'company', 'position', 'start_date', 'end_date', 'is_current', 'location')
    list_filter = ('is_current', 'start_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'company', 'position', 'location')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """
    Admin interface for Portfolio model.
    """
    list_display = ('user', 'title', 'is_featured', 'start_date', 'created_at')
    list_filter = ('is_featured', 'start_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    """
    Admin interface for SocialLink model.
    """
    list_display = ('user', 'platform', 'url', 'is_public', 'created_at')
    list_filter = ('platform', 'is_public', 'created_at')
    search_fields = ('user__username', 'user__email', 'url')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """
    Admin interface for UserPreferences model.
    """
    list_display = ('user', 'email_job_alerts', 'profile_visibility', 'alert_frequency', 'updated_at')
    list_filter = ('email_job_alerts', 'profile_visibility', 'alert_frequency', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Email Notifications', {
            'fields': ('email_job_alerts', 'email_application_updates', 'email_new_jobs', 'email_newsletter')
        }),
        ('Job Alerts', {
            'fields': ('alert_frequency',)
        }),
        ('Privacy Settings', {
            'fields': ('profile_visibility', 'show_email', 'show_phone', 'show_location', 'resume_visibility')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    """
    Admin interface for SavedJob model.
    """
    list_display = ('user', 'job', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'job__title', 'job__employer__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user', 'job', 'job__employer')
