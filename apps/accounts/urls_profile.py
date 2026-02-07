"""
URL configuration for user profile endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_profile

app_name = 'accounts_profile'

# Router for ViewSets
router = DefaultRouter()
router.register(r'skills', views_profile.SkillViewSet, basename='skill')
router.register(r'education', views_profile.EducationViewSet, basename='education')
router.register(r'work-history', views_profile.WorkHistoryViewSet, basename='work-history')
router.register(r'portfolio', views_profile.PortfolioViewSet, basename='portfolio')
router.register(r'social-links', views_profile.SocialLinkViewSet, basename='social-link')
router.register(r'preferences', views_profile.UserPreferencesViewSet, basename='preferences')
router.register(r'saved-jobs', views_profile.SavedJobViewSet, basename='saved-job')

urlpatterns = [
    # Profile endpoints
    path('profile/', views_profile.user_profile, name='user-profile'),
    path('dashboard/', views_profile.user_dashboard, name='user-dashboard'),
] + router.urls
