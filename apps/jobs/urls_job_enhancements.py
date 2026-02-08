"""
URL configuration for job enhancement endpoints.
"""
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views_job_enhancements

app_name = 'jobs_enhancements'

# Router for ViewSets
router = SimpleRouter()
router.register(r'shares', views_job_enhancements.JobShareViewSet, basename='job-share')

urlpatterns = [
    # Job enhancement endpoints
    path('share/', views_job_enhancements.share_job, name='share-job'),
    path('similar/', views_job_enhancements.similar_jobs, name='similar-jobs'),
    path('recommendations/', views_job_enhancements.job_recommendations, name='job-recommendations'),
    path('<uuid:job_id>/analytics/', views_job_enhancements.job_analytics, name='job-analytics'),
    path('employer/dashboard/', views_job_enhancements.employer_dashboard, name='employer-dashboard'),
] + router.urls
