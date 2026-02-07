"""
URL configuration for data export endpoints.
"""
from django.urls import path
from . import views_export

app_name = 'export'

urlpatterns = [
    path('jobs/', views_export.export_jobs, name='export-jobs'),
    path('applications/', views_export.export_applications, name='export-applications'),
    path('users/', views_export.export_users, name='export-users'),
]
