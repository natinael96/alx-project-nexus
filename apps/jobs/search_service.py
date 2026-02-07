"""
Advanced search service with fuzzy matching, ranking, and analytics.
"""
import logging
from typing import Dict, List, Optional, Tuple
from django.db.models import Q, F, Count, Case, When, IntegerField
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank
)

# Try to import trigram functions (PostgreSQL extension)
try:
    from django.contrib.postgres.search import TrigramSimilarity, TrigramDistance
    TRIGRAM_AVAILABLE = True
except ImportError:
    TRIGRAM_AVAILABLE = False
    TrigramSimilarity = None  # Placeholder
from django.db import connection
from django.utils import timezone
from django.core.cache import cache
from apps.jobs.models import Job, Category
from apps.jobs.models_search import SearchHistory, SavedSearch, PopularSearchTerm
from apps.core.cache_utils import CacheKeyBuilder
from apps.core.storage import storage_manager

logger = logging.getLogger(__name__)


class AdvancedSearchService:
    """
    Advanced search service with fuzzy matching, ranking, and result boosting.
    """
    
    @staticmethod
    def search_jobs(
        query: str,
        filters: Optional[Dict] = None,
        user: Optional = None,
        boost_featured: bool = True,
        boost_recent: bool = True,
        fuzzy_threshold: float = 0.3
    ) -> Tuple[List, int]:
        """
        Perform advanced search on jobs with ranking and boosting.
        
        Args:
            query: Search query string
            filters: Additional filters (category, location, etc.)
            user: User performing the search (for history tracking)
            boost_featured: Whether to boost featured jobs
            boost_recent: Whether to boost recently posted jobs
            fuzzy_threshold: Threshold for fuzzy matching (0.0 to 1.0)
            
        Returns:
            Tuple of (queryset, total_count)
        """
        filters = filters or {}
        
        # Start with base queryset
        queryset = Job.objects.select_related('category', 'employer').prefetch_related('applications')
        
        # Apply status filter (security)
        if not user or not (user.is_employer or user.is_admin):
            queryset = queryset.filter(status='active')
        elif filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        
        # Apply additional filters
        if filters.get('category'):
            queryset = queryset.filter(category_id=filters['category'])
        if filters.get('location'):
            queryset = queryset.filter(location__icontains=filters['location'])
        if filters.get('job_type'):
            queryset = queryset.filter(job_type=filters['job_type'])
        if filters.get('min_salary'):
            queryset = queryset.filter(salary_min__gte=filters['min_salary'])
        if filters.get('max_salary'):
            queryset = queryset.filter(salary_max__lte=filters['max_salary'])
        if filters.get('is_featured') is not None:
            queryset = queryset.filter(is_featured=filters['is_featured'])
        
        # Perform search if query provided
        if query and query.strip():
            search_term = query.strip()
            
            # Check if PostgreSQL full-text search is available
            if connection.vendor == 'postgresql':
                queryset = AdvancedSearchService._postgresql_search(
                    queryset, search_term, boost_featured, boost_recent
                )
            else:
                # Fallback to basic search
                queryset = AdvancedSearchService._basic_search(queryset, search_term)
        
        # Apply ranking and boosting
        if query and query.strip():
            queryset = AdvancedSearchService._apply_ranking(
                queryset, query.strip(), boost_featured, boost_recent
            )
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Track search history
        if user or query:
            AdvancedSearchService._track_search(query or '', filters, user, total_count)
        
        return queryset, total_count
    
    @staticmethod
    def _postgresql_search(queryset, search_term: str, boost_featured: bool, boost_recent: bool):
        """Perform PostgreSQL full-text search."""
        try:
            # Create search vector from multiple fields
            search_vector = (
                SearchVector('title', weight='A', config='english') +
                SearchVector('description', weight='B', config='english') +
                SearchVector('requirements', weight='B', config='english') +
                SearchVector('location', weight='C', config='english')
            )
            
            # Create search query
            search_query = SearchQuery(search_term, config='english')
            
            # Add search vector and rank
            queryset = queryset.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query)
            
            # Order by rank
            queryset = queryset.order_by('-rank', '-created_at')
            
        except Exception as e:
            logger.warning(f"PostgreSQL search failed, falling back to basic search: {e}")
            queryset = AdvancedSearchService._basic_search(queryset, search_term)
        
        return queryset
    
    @staticmethod
    def _basic_search(queryset, search_term: str):
        """Basic search using icontains (fallback)."""
        return queryset.filter(
            Q(title__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(requirements__icontains=search_term) |
            Q(location__icontains=search_term)
        )
    
    @staticmethod
    def _apply_ranking(queryset, search_term: str, boost_featured: bool, boost_recent: bool):
        """Apply custom ranking and boosting to search results."""
        # Calculate relevance score
        # Boost title matches
        title_match = Case(
            When(title__icontains=search_term, then=10),
            default=0,
            output_field=IntegerField()
        )
        
        # Boost featured jobs
        featured_boost = Case(
            When(is_featured=True, then=5) if boost_featured else When(pk__isnull=False, then=0),
            default=0,
            output_field=IntegerField()
        )
        
        # Boost recent jobs (within last 7 days)
        recent_boost = Case(
            When(created_at__gte=timezone.now() - timezone.timedelta(days=7), then=3) if boost_recent else When(pk__isnull=False, then=0),
            default=0,
            output_field=IntegerField()
        )
        
        # Boost jobs with more views (popularity)
        views_boost = Case(
            When(views_count__gt=100, then=2),
            When(views_count__gt=50, then=1),
            default=0,
            output_field=IntegerField()
        )
        
        # Annotate with relevance score
        queryset = queryset.annotate(
            relevance_score=title_match + featured_boost + recent_boost + views_boost
        )
        
        # Order by relevance score, then by created_at
        queryset = queryset.order_by('-relevance_score', '-created_at')
        
        return queryset
    
    @staticmethod
    def _track_search(query: str, filters: Dict, user, result_count: int):
        """Track search in history and update popular terms."""
        try:
            # Track search history
            if user and user.is_authenticated:
                SearchHistory.objects.create(
                    user=user,
                    search_query=query,
                    filters=filters,
                    result_count=result_count
                )
            else:
                # Track anonymous searches (optional)
                SearchHistory.objects.create(
                    search_query=query,
                    filters=filters,
                    result_count=result_count
                )
            
            # Update popular search terms
            if query and len(query.strip()) >= 2:
                term = query.strip().lower()
                popular_term, created = PopularSearchTerm.objects.get_or_create(
                    term=term,
                    defaults={'search_count': 1}
                )
                if not created:
                    popular_term.search_count += 1
                    popular_term.save(update_fields=['search_count', 'last_searched_at'])
        
        except Exception as e:
            logger.error(f"Error tracking search: {e}")


class SearchAutocompleteService:
    """
    Service for search autocomplete and suggestions.
    """
    
    @staticmethod
    def get_autocomplete_suggestions(query: str, limit: int = 10) -> List[Dict]:
        """
        Get autocomplete suggestions based on search query.
        
        Args:
            query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggestion dictionaries
        """
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip().lower()
        suggestions = []
        
        try:
            # Get suggestions from popular search terms
            popular_terms = PopularSearchTerm.objects.filter(
                term__icontains=query
            ).order_by('-search_count', '-last_searched_at')[:limit]
            
            for term in popular_terms:
                suggestions.append({
                    'text': term.term,
                    'type': 'popular',
                    'count': term.search_count
                })
            
            # Get suggestions from job titles
            job_titles = Job.objects.filter(
                title__icontains=query,
                status='active'
            ).values_list('title', flat=True).distinct()[:limit]
            
            for title in job_titles:
                if title.lower() not in [s['text'].lower() for s in suggestions]:
                    suggestions.append({
                        'text': title,
                        'type': 'job_title'
                    })
            
            # Get suggestions from locations
            locations = Job.objects.filter(
                location__icontains=query,
                status='active'
            ).values_list('location', flat=True).distinct()[:limit]
            
            for location in locations:
                if location.lower() not in [s['text'].lower() for s in suggestions]:
                    suggestions.append({
                        'text': location,
                        'type': 'location'
                    })
            
            # Limit total suggestions
            return suggestions[:limit]
        
        except Exception as e:
            logger.error(f"Error getting autocomplete suggestions: {e}")
            return []
    
    @staticmethod
    def get_search_suggestions(query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions (similar searches).
        
        Args:
            query: Search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested search terms
        """
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip().lower()
        suggestions = []
        
        try:
            # Use trigram similarity for fuzzy matching (PostgreSQL)
            if connection.vendor == 'postgresql' and TRIGRAM_AVAILABLE:
                try:
                    similar_terms = PopularSearchTerm.objects.annotate(
                        similarity=TrigramSimilarity('term', query)
                    ).filter(
                        similarity__gt=0.3
                    ).exclude(
                        term=query
                    ).order_by('-similarity', '-search_count')[:limit]
                    
                    suggestions = [term.term for term in similar_terms]
                except Exception as e:
                    logger.warning(f"Trigram search failed, using fallback: {e}")
                    # Fall through to fallback
                    pass
            
            if not suggestions:
                # Fallback: simple contains match
                similar_terms = PopularSearchTerm.objects.filter(
                    term__icontains=query
                ).exclude(
                    term=query
                ).order_by('-search_count')[:limit]
                
                suggestions = [term.term for term in similar_terms]
        
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
        
        return suggestions


class SearchAnalyticsService:
    """
    Service for search analytics and reporting.
    """
    
    @staticmethod
    def get_popular_search_terms(limit: int = 10, days: int = 30) -> List[Dict]:
        """
        Get most popular search terms.
        
        Args:
            limit: Number of terms to return
            days: Number of days to look back
            
        Returns:
            List of popular search terms with counts
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        popular_terms = PopularSearchTerm.objects.filter(
            last_searched_at__gte=cutoff_date
        ).order_by('-search_count', '-last_searched_at')[:limit]
        
        return [
            {
                'term': term.term,
                'count': term.search_count,
                'last_searched': term.last_searched_at
            }
            for term in popular_terms
        ]
    
    @staticmethod
    def get_search_statistics(days: int = 30) -> Dict:
        """
        Get search statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with search statistics
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        total_searches = SearchHistory.objects.filter(created_at__gte=cutoff_date).count()
        unique_searches = SearchHistory.objects.filter(
            created_at__gte=cutoff_date
        ).values('search_query').distinct().count()
        
        avg_results = SearchHistory.objects.filter(
            created_at__gte=cutoff_date
        ).aggregate(avg=Count('result_count'))['avg'] or 0
        
        searches_by_user = SearchHistory.objects.filter(
            created_at__gte=cutoff_date,
            user__isnull=False
        ).values('user').distinct().count()
        
        return {
            'total_searches': total_searches,
            'unique_searches': unique_searches,
            'average_results': avg_results,
            'searches_by_users': searches_by_user,
            'period_days': days,
        }
    
    @staticmethod
    def get_user_search_history(user, limit: int = 20) -> List[Dict]:
        """
        Get user's search history.
        
        Args:
            user: User object
            limit: Maximum number of history items
            
        Returns:
            List of search history items
        """
        history = SearchHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:limit]
        
        return [
            {
                'query': item.search_query,
                'filters': item.filters,
                'result_count': item.result_count,
                'created_at': item.created_at
            }
            for item in history
        ]
