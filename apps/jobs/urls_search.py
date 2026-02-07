"""
URL configuration for search endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views_search

app_name = 'jobs_search'

# Router for ViewSets
router = DefaultRouter()
router.register(r'saved-searches', views_search.SavedSearchViewSet, basename='saved-search')
router.register(r'search-alerts', views_search.SearchAlertViewSet, basename='search-alert')

urlpatterns = [
    # Search endpoints
    path('autocomplete/', views_search.search_autocomplete, name='search-autocomplete'),
    path('suggestions/', views_search.search_suggestions, name='search-suggestions'),
    path('history/', views_search.user_search_history, name='user-search-history'),
    path('popular-terms/', views_search.popular_search_terms, name='popular-search-terms'),
    path('statistics/', views_search.search_statistics, name='search-statistics'),
] + router.urls
