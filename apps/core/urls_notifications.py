"""
URL configuration for notification endpoints.
"""
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views_notifications

app_name = 'notifications'

# Router for ViewSets
router = SimpleRouter()
router.register(r'', views_notifications.NotificationViewSet, basename='notification')
router.register(r'preferences', views_notifications.NotificationPreferenceViewSet, basename='notification-preference')

urlpatterns = [
    # Notification endpoints
    path('summary/', views_notifications.notification_summary, name='notification-summary'),
] + router.urls
