"""
URL configuration for jobs app - Job endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, ApplicationViewSet

app_name = 'jobs'

router = DefaultRouter()
router.register(r'', JobViewSet, basename='job')
router.register(r'applications', ApplicationViewSet, basename='job-application')

urlpatterns = [
    path('', include(router.urls)),
]

