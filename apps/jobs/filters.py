"""
Filters for jobs app.
"""
import django_filters
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
    # Note: 'search' is intentionally NOT defined here to avoid duplicating
    # the 'search' query parameter that DRF's SearchFilter already generates.
    # SearchFilter handles search via JobViewSet.search_fields.
    
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

