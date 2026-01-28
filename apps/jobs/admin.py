"""
Admin configuration for jobs app.
"""
from django.contrib import admin
from .models import Job, Category, Application


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""
    list_display = ('name', 'parent', 'slug', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin interface for Job model."""
    list_display = (
        'title', 'employer', 'category', 'location',
        'job_type', 'status', 'is_featured', 'views_count', 'created_at'
    )
    list_filter = ('status', 'job_type', 'category', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'location', 'employer__username')
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'requirements', 'category', 'employer')
        }),
        ('Job Details', {
            'fields': ('location', 'job_type', 'salary_min', 'salary_max', 'application_deadline')
        }),
        ('Status & Settings', {
            'fields': ('status', 'is_featured', 'views_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Application model."""
    list_display = (
        'applicant', 'job', 'status', 'applied_at', 'reviewed_at'
    )
    list_filter = ('status', 'applied_at', 'reviewed_at')
    search_fields = (
        'applicant__username', 'applicant__email',
        'job__title', 'cover_letter'
    )
    readonly_fields = ('applied_at',)
    fieldsets = (
        ('Application Information', {
            'fields': ('job', 'applicant', 'cover_letter', 'resume')
        }),
        ('Status & Review', {
            'fields': ('status', 'notes', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('applied_at',),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-applied_at',)

