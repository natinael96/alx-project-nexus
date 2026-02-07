"""
URL configuration for core app - Health checks and monitoring.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Health checks
    path('', views.health_check_view, name='health-check'),
    path('liveness/', views.liveness_check_view, name='liveness-check'),
    path('readiness/', views.readiness_check_view, name='readiness-check'),
    
    # Analytics and statistics (Admin only)
    path('statistics/', views.statistics_view, name='statistics'),
    path('statistics/users/', views.user_statistics_view, name='user-statistics'),
    path('statistics/jobs/', views.job_statistics_view, name='job-statistics'),
    path('statistics/applications/', views.application_statistics_view, name='application-statistics'),
    path('statistics/user-activity/', views.user_activity_view, name='user-activity'),
]
