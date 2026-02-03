"""
Filters for jobs app.
"""
import django_filters
from django.db import models
from .models import Job, Category, Application


class JobFilter(django_filters.FilterSet):
    """
    Filter set for Job model.
    
    Security: Status filtering is restricted to authenticated users only.
    Non-authenticated users can only see active jobs.
    """
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    location = django_filters.CharFilter(lookup_expr='icontains')
    job_type = django_filters.ChoiceFilter(choices=Job.JOB_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=Job.STATUS_CHOICES)
    min_salary = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    max_salary = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    is_featured = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Job
        fields = ['category', 'location', 'job_type', 'status', 'is_featured']
    
    def filter_queryset(self, queryset):
        """Override to enforce security on status filtering."""
        # Get the request from the view
        request = getattr(self, 'request', None)
        
        # If no request or user is not authenticated, force status='active'
        if not request or not request.user.is_authenticated:
            # Remove status from filters if present
            if 'status' in self.form.cleaned_data:
                self.form.cleaned_data.pop('status')
            # Force active status for non-authenticated users
            queryset = queryset.filter(status='active')
        
        # Apply other filters
        return super().filter_queryset(queryset)
    
    def filter_search(self, queryset, name, value):
        """
        Full-text search on title, description, and requirements.
        
        Security: Uses parameterized queries (Django ORM) to prevent SQL injection.
        Performance: Uses case-insensitive contains for flexible matching.
        """
        if value:
            # Strip and validate search term
            search_term = value.strip()
            if len(search_term) < 2:
                # Too short search terms can be inefficient, but allow them
                pass
            
            # Use Q objects for OR logic (safe from SQL injection)
            return queryset.filter(
                models.Q(title__icontains=search_term) |
                models.Q(description__icontains=search_term) |
                models.Q(requirements__icontains=search_term) |
                models.Q(location__icontains=search_term)  # Also search location
            )
        return queryset


class ApplicationFilter(django_filters.FilterSet):
    """
    Filter set for Application model.
    
    Security: Filters are applied after role-based queryset filtering.
    Only shows applications accessible to the current user.
    """
    status = django_filters.ChoiceFilter(choices=Application.STATUS_CHOICES)
    job = django_filters.ModelChoiceFilter(
        queryset=Job.objects.all(),
        help_text='Filter by job ID'
    )
    
    class Meta:
        model = Application
        fields = ['status', 'job']
    
    def filter_queryset(self, queryset):
        """
        Apply filters to queryset.
        
        Note: Role-based filtering is handled in the ViewSet's get_queryset method.
        This filter only applies additional filters on the already-filtered queryset.
        """
        return super().filter_queryset(queryset)

