"""
Admin configuration for job enhancement models.
"""
from django.contrib import admin
from .models_job_enhancements import (
    JobView, JobShare, JobRecommendation, JobAnalytics, ApplicationSource
)


@admin.register(JobView)
class JobViewAdmin(admin.ModelAdmin):
    """
    Admin interface for JobView model.
    """
    list_display = ('job', 'user_display', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('job__title', 'user__username', 'user__email', 'ip_address')
    readonly_fields = ('viewed_at',)
    date_hierarchy = 'viewed_at'
    
    def user_display(self, obj):
        """Display user or Anonymous."""
        return obj.user.username if obj.user else 'Anonymous'
    user_display.short_description = 'User'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('job', 'user')


@admin.register(JobShare)
class JobShareAdmin(admin.ModelAdmin):
    """
    Admin interface for JobShare model.
    """
    list_display = ('job', 'user', 'method', 'shared_with', 'shared_at')
    list_filter = ('method', 'shared_at')
    search_fields = ('job__title', 'user__username', 'shared_with')
    readonly_fields = ('shared_at',)
    date_hierarchy = 'shared_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('job', 'user')


@admin.register(JobRecommendation)
class JobRecommendationAdmin(admin.ModelAdmin):
    """
    Admin interface for JobRecommendation model.
    """
    list_display = ('user', 'job', 'score', 'viewed', 'clicked', 'created_at')
    list_filter = ('viewed', 'clicked', 'created_at')
    search_fields = ('user__username', 'job__title', 'reason')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user', 'job')


@admin.register(JobAnalytics)
class JobAnalyticsAdmin(admin.ModelAdmin):
    """
    Admin interface for JobAnalytics model.
    """
    list_display = ('job', 'total_views', 'unique_views', 'total_applications', 'shares_count', 'saved_count', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('job__title', 'job__employer__username')
    readonly_fields = ('last_updated',)
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('job', 'job__employer')


@admin.register(ApplicationSource)
class ApplicationSourceAdmin(admin.ModelAdmin):
    """
    Admin interface for ApplicationSource model.
    """
    list_display = ('application', 'source_type', 'utm_source', 'utm_medium', 'campaign', 'created_at')
    list_filter = ('source_type', 'created_at')
    search_fields = ('application__job__title', 'utm_source', 'utm_medium', 'campaign')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('application', 'application__job')
