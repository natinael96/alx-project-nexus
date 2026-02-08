"""
URL configuration for jobs app - Category endpoints.
"""
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet

app_name = 'categories'

router = SimpleRouter()
router.register(r'', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]

