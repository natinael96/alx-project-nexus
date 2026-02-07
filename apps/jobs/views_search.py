"""
Search-related views for advanced search features.
"""
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from apps.jobs.models_search import SearchHistory, SavedSearch, SearchAlert, PopularSearchTerm
from apps.jobs.serializers_search import SavedSearchSerializer, SearchAlertSerializer
from apps.jobs.search_service import (
    AdvancedSearchService,
    SearchAutocompleteService,
    SearchAnalyticsService
)
from apps.accounts.permissions import IsAdminUser
from apps.core.rate_limit import rate_limit, RATE_LIMITS, rate_limit_search
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='get',
    operation_summary='Search autocomplete',
    operation_description='Get autocomplete suggestions based on partial search query. Returns popular terms, job titles, and locations.',
    manual_parameters=[
        openapi.Parameter(
            'q',
            openapi.IN_QUERY,
            description='Partial search query (minimum 2 characters)',
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description='Maximum number of suggestions (default: 10)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: openapi.Response('Autocomplete suggestions'),
        400: 'Bad Request - Query too short',
    }
)
@rate_limit(
    limit=RATE_LIMITS['search']['limit'],
    period=RATE_LIMITS['search']['period'],
    key_func=rate_limit_search,
    scope='autocomplete'
)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_autocomplete(request):
    """Get autocomplete suggestions for search."""
    query = request.query_params.get('q', '').strip()
    limit = int(request.query_params.get('limit', 10))
    
    if len(query) < 2:
        return Response(
            {'error': 'Query must be at least 2 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    suggestions = SearchAutocompleteService.get_autocomplete_suggestions(query, limit)
    
    return Response({
        'query': query,
        'suggestions': suggestions,
        'count': len(suggestions)
    })


@swagger_auto_schema(
    method='get',
    operation_summary='Get search suggestions',
    operation_description='Get similar search suggestions based on query. Uses fuzzy matching to find similar popular searches.',
    manual_parameters=[
        openapi.Parameter(
            'q',
            openapi.IN_QUERY,
            description='Search query',
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description='Maximum number of suggestions (default: 5)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: openapi.Response('Search suggestions'),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):
    """Get search suggestions (similar searches)."""
    query = request.query_params.get('q', '').strip()
    limit = int(request.query_params.get('limit', 5))
    
    suggestions = SearchAutocompleteService.get_search_suggestions(query, limit)
    
    return Response({
        'query': query,
        'suggestions': suggestions
    })


@swagger_auto_schema(
    method='get',
    operation_summary='Get user search history',
    operation_description='Get the authenticated user\'s search history. Returns recent searches with filters and result counts.',
    responses={
        200: openapi.Response('Search history'),
        401: 'Unauthorized',
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_search_history(request):
    """Get user's search history."""
    limit = int(request.query_params.get('limit', 20))
    
    history = SearchAnalyticsService.get_user_search_history(request.user, limit)
    
    return Response({
        'history': history,
        'count': len(history)
    })


@swagger_auto_schema(
    method='get',
    operation_summary='Get popular search terms',
    operation_description='Get most popular search terms. Public access.',
    manual_parameters=[
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description='Number of terms to return (default: 10)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'days',
            openapi.IN_QUERY,
            description='Number of days to look back (default: 30)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: openapi.Response('Popular search terms'),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def popular_search_terms(request):
    """Get popular search terms."""
    limit = int(request.query_params.get('limit', 10))
    days = int(request.query_params.get('days', 30))
    
    terms = SearchAnalyticsService.get_popular_search_terms(limit, days)
    
    return Response({
        'terms': terms,
        'count': len(terms)
    })


@swagger_auto_schema(
    method='get',
    operation_summary='Get search statistics',
    operation_description='Get search analytics and statistics. Admin only.',
    manual_parameters=[
        openapi.Parameter(
            'days',
            openapi.IN_QUERY,
            description='Number of days to analyze (default: 30)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: openapi.Response('Search statistics'),
        403: 'Forbidden - Admin access required',
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def search_statistics(request):
    """Get search statistics (admin only)."""
    days = int(request.query_params.get('days', 30))
    
    stats = SearchAnalyticsService.get_search_statistics(days)
    
    return Response(stats)


class SavedSearchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved searches.
    """
    queryset = SavedSearch.objects.all()
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's saved searches."""
        return SavedSearch.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating a saved search."""
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        method='post',
        operation_summary='Execute saved search',
        operation_description='Execute a saved search and return results. Updates last_searched_at timestamp.',
        responses={
            200: 'Search results',
            404: 'Saved search not found',
        }
    )
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a saved search."""
        saved_search = self.get_object()
        
        # Update last searched timestamp
        saved_search.last_searched_at = timezone.now()
        saved_search.save(update_fields=['last_searched_at'])
        
        # Perform search
        queryset, total_count = AdvancedSearchService.search_jobs(
            query=saved_search.search_query,
            filters=saved_search.filters,
            user=request.user
        )
        
        # Serialize results (using JobListSerializer)
        from apps.jobs.serializers import JobListSerializer
        from rest_framework.pagination import PageNumberPagination
        
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = JobListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = JobListSerializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': total_count
        })


class SearchAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing search alerts.
    """
    queryset = SearchAlert.objects.all()
    serializer_class = SearchAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's search alerts."""
        return SearchAlert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating a search alert."""
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        method='post',
        operation_summary='Toggle alert active status',
        operation_description='Toggle the active status of a search alert.',
        responses={
            200: 'Alert status updated',
            404: 'Alert not found',
        }
    )
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle alert active status."""
        alert = self.get_object()
        alert.is_active = not alert.is_active
        alert.save(update_fields=['is_active'])
        
        return Response({
            'id': alert.id,
            'is_active': alert.is_active,
            'message': f'Alert {"activated" if alert.is_active else "deactivated"}'
        })
