"""
URL configuration for accounts app.
"""
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views_security import (
    password_reset_request,
    password_reset_confirm,
    APIKeyViewSet,
    IPWhitelistViewSet,
)
from .views_oauth import oauth_login_url, oauth_callback

app_name = 'accounts'

router = SimpleRouter()
router.register(r'api-keys', APIKeyViewSet, basename='api-key')
router.register(r'ip-whitelist', IPWhitelistViewSet, basename='ip-whitelist')

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('refresh/', views.refresh_token, name='refresh'),
    path('me/', views.get_current_user, name='current-user'),
    path('me/update/', views.update_current_user, name='update-user'),
    path('change-password/', views.change_password, name='change-password'),
    
    # Password reset
    path('password-reset/', password_reset_request, name='password-reset-request'),
    path('password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
    
    # OAuth2 / Social login
    path('oauth/login-url/', oauth_login_url, name='oauth-login-url'),
    path('oauth/callback/', oauth_callback, name='oauth-callback'),
    
    # User management (Admin only)
    path('users/', views.UserListAPIView.as_view(), name='user-list'),
    path('users/<uuid:pk>/', views.UserDetailAPIView.as_view(), name='user-detail'),
    
    # Profile endpoints
    path('profile/', include('apps.accounts.urls_profile')),
    
    # Security endpoints
    path('', include(router.urls)),
]

