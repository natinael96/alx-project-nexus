"""
Filters for jobs app.
"""
import django_filters
from django.db import models
from .models import Job, Category, Application


class JobFilter(django_filters.FilterSet):
    """Filter set for Job model."""
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
    
    def filter_search(self, queryset, name, value):
        """Full-text search on title and description."""
        if value:
            return queryset.filter(
                models.Q(title__icontains=value) |
                models.Q(description__icontains=value) |
                models.Q(requirements__icontains=value)
            )
        return queryset


class ApplicationFilter(django_filters.FilterSet):
    """Filter set for Application model."""
    status = django_filters.ChoiceFilter(choices=Application.STATUS_CHOICES)
    job = django_filters.ModelChoiceFilter(queryset=Job.objects.all())
    
    class Meta:
        model = Application
        fields = ['status', 'job']

