"""
Admin configuration for jobs app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Job, Category, Application

# Import enhancement admins
from . import admin_job_enhancements  # noqa
from . import admin_application_enhancements  # noqa

# Import search admin
from . import admin_search  # noqa


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model.
    
    Features:
    - Hierarchical category display
    - Job count per category
    - Automatic slug generation
    """
    list_display = ('name', 'parent', 'job_count_display', 'slug', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'slug')
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'description', 'parent', 'slug')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with job count annotation."""
        qs = super().get_queryset(request)
        return qs.select_related('parent').annotate(
            job_count=Count('jobs')
        )
    
    def job_count_display(self, obj):
        """Display job count for category."""
        count = getattr(obj, 'job_count', obj.jobs.count())
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            count
        )
    job_count_display.short_description = 'Jobs'
    job_count_display.admin_order_field = 'job_count'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """
    Admin interface for Job model.
    
    Features:
    - Comprehensive job management
    - Application count display
    - Status and featured filtering
    - Optimized queries
    """
    list_display = (
        'title', 'employer', 'category', 'location',
        'job_type', 'status_display', 'is_featured', 
        'application_count_display', 'views_count', 'created_at'
    )
    list_filter = ('status', 'job_type', 'category', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'location', 'employer__username', 'employer__email')
    readonly_fields = ('views_count', 'created_at', 'updated_at', 'application_count_display')
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'requirements', 'category', 'employer')
        }),
        ('Job Details', {
            'fields': ('location', 'job_type', 'salary_min', 'salary_max', 'application_deadline')
        }),
        ('Status & Settings', {
            'fields': ('status', 'is_featured', 'views_count', 'application_count_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        """Optimize queryset with related objects and counts."""
        qs = super().get_queryset(request)
        return qs.select_related('category', 'employer').prefetch_related('applications').annotate(
            application_count=Count('applications')
        )
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'draft': 'gray',
            'active': 'green',
            'closed': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def application_count_display(self, obj):
        """Display application count."""
        count = getattr(obj, 'application_count', obj.applications.count())
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            count
        )
    application_count_display.short_description = 'Applications'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """
    Admin interface for Application model.
    
    Features:
    - Application status management
    - Resume file download
    - Status filtering and search
    - Optimized queries
    """
    list_display = (
        'applicant', 'job_title_display', 'status_display', 
        'applied_at', 'reviewed_at', 'resume_link'
    )
    list_filter = ('status', 'applied_at', 'reviewed_at', 'job__category')
    search_fields = (
        'applicant__username', 'applicant__email', 'applicant__first_name', 'applicant__last_name',
        'job__title', 'cover_letter', 'notes'
    )
    readonly_fields = ('applied_at', 'resume_download')
    list_per_page = 50
    date_hierarchy = 'applied_at'
    
    fieldsets = (
        ('Application Information', {
            'fields': ('job', 'applicant', 'cover_letter', 'resume', 'resume_download')
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
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('job', 'applicant', 'job__category', 'job__employer')
    
    def job_title_display(self, obj):
        """Display job title with link."""
        return format_html(
            '<a href="/admin/jobs/job/{}/change/">{}</a>',
            obj.job.id,
            obj.job.title[:50] + '...' if len(obj.job.title) > 50 else obj.job.title
        )
    job_title_display.short_description = 'Job'
    job_title_display.admin_order_field = 'job__title'
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'pending': 'orange',
            'reviewed': 'blue',
            'accepted': 'green',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def resume_link(self, obj):
        """Display resume download link."""
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank">Download</a>',
                obj.resume.url
            )
        return '-'
    resume_link.short_description = 'Resume'
    
    def resume_download(self, obj):
        """Display resume download in detail view."""
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank" style="padding: 5px 10px; background: #007cba; color: white; text-decoration: none; border-radius: 3px;">Download Resume</a>',
                obj.resume.url
            )
        return 'No resume uploaded'
    resume_download.short_description = 'Resume File'

