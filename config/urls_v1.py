"""
URL configuration for API v1.
"""
from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # API v1 endpoints
    path('auth/', include('apps.accounts.urls')),
    path('jobs/', include('apps.jobs.urls_job_enhancements')),
    path('jobs/', include('apps.jobs.urls')),
    path('categories/', include('apps.jobs.urls_category')),
    path('applications/', include('apps.jobs.urls_application')),
    path('applications/', include('apps.jobs.urls_application_enhancements')),
    path('search/', include('apps.jobs.urls_search')),
    path('notifications/', include('apps.core.urls_notifications')),
    path('export/', include('apps.core.urls_export')),
    path('audit/', include('apps.core.urls_audit')),
]
