"""
URL configuration for audit logging endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_audit

app_name = 'audit'

# Router for ViewSets
router = DefaultRouter()
router.register(r'logs', views_audit.AuditLogViewSet, basename='audit-log')
router.register(r'history', views_audit.ChangeHistoryViewSet, basename='change-history')

urlpatterns = [
    # Audit endpoints
    path('object-history/', views_audit.object_history, name='object-history'),
] + router.urls
