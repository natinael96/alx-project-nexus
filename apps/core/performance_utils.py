"""
Performance optimization utilities.
"""
import logging
from functools import wraps
from django.db import connection, reset_queries
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def detect_n_plus_one(func):
    """
    Decorator to detect N+1 query problems.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if settings.DEBUG:
            reset_queries()
            initial_queries = len(connection.queries)
            
            result = func(*args, **kwargs)
            
            final_queries = len(connection.queries)
            query_count = final_queries - initial_queries
            
            if query_count > 10:  # Threshold for potential N+1
                logger.warning(
                    f"Potential N+1 query detected in {func.__name__}: "
                    f"{query_count} queries executed"
                )
                if settings.DEBUG:
                    # Log queries in debug mode
                    for query in connection.queries[initial_queries:]:
                        logger.debug(f"Query: {query['sql']}")
            
            return result
        return func(*args, **kwargs)
    return wrapper


def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """
    Optimize a queryset with select_related and prefetch_related.
    
    Args:
        queryset: Django queryset
        select_related: List of fields for select_related
        prefetch_related: List of fields for prefetch_related
    
    Returns:
        Optimized queryset
    """
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    
    return queryset


class QueryCounter:
    """
    Context manager for counting database queries.
    """
    def __init__(self):
        self.initial_queries = 0
        self.final_queries = 0
    
    def __enter__(self):
        if settings.DEBUG:
            reset_queries()
            self.initial_queries = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if settings.DEBUG:
            self.final_queries = len(connection.queries)
            query_count = self.final_queries - self.initial_queries
            
            if query_count > 0:
                logger.info(f"Executed {query_count} database queries")
                
                if query_count > 10:
                    logger.warning(f"High query count detected: {query_count}")
        
        return False
    
    @property
    def count(self):
        """Get the number of queries executed."""
        if settings.DEBUG:
            return self.final_queries - self.initial_queries
        return 0
