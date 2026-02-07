"""
URL configuration for accounts app.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('refresh/', views.refresh_token, name='refresh'),
    path('me/', views.get_current_user, name='current-user'),
    path('me/update/', views.update_current_user, name='update-user'),
    path('change-password/', views.change_password, name='change-password'),
    
    # User management (Admin only)
    path('users/', views.UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailAPIView.as_view(), name='user-detail'),
    
    # Profile endpoints
    path('profile/', include('apps.accounts.urls_profile')),
]

