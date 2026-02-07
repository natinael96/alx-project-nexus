"""
Cache utility functions and key naming strategies.
"""
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
from functools import wraps
from typing import Optional, Any, Callable


class CacheKeyBuilder:
    """
    Utility class for building consistent cache keys.
    """
    
    PREFIX = getattr(settings, 'CACHE_KEY_PREFIX', 'jobboard')
    
    @classmethod
    def build_key(cls, *parts: str, version: Optional[int] = None) -> str:
        """
        Build a cache key from parts.
        
        Args:
            *parts: Key parts to join
            version: Optional version number for cache invalidation
            
        Returns:
            Formatted cache key
        """
        key_parts = [cls.PREFIX] + list(parts)
        if version:
            key_parts.append(f'v{version}')
        return ':'.join(str(part) for part in key_parts if part)
    
    @classmethod
    def build_key_from_dict(cls, prefix: str, data: dict, version: Optional[int] = None) -> str:
        """
        Build a cache key from a dictionary by hashing the data.
        Useful for complex query parameters.
        
        Args:
            prefix: Key prefix
            data: Dictionary to hash
            version: Optional version number
            
        Returns:
            Formatted cache key with hash
        """
        # Sort and stringify dict for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(sorted_data.encode()).hexdigest()[:8]
        return cls.build_key(prefix, data_hash, version=version)
    
    # Predefined key builders
    @classmethod
    def category_list(cls, version: Optional[int] = None) -> str:
        """Cache key for category list."""
        return cls.build_key('categories', 'list', version=version)
    
    @classmethod
    def category_detail(cls, category_id: int, version: Optional[int] = None) -> str:
        """Cache key for category detail."""
        return cls.build_key('categories', 'detail', str(category_id), version=version)
    
    @classmethod
    def featured_jobs(cls, limit: int = 10, version: Optional[int] = None) -> str:
        """Cache key for featured jobs."""
        return cls.build_key('jobs', 'featured', str(limit), version=version)
    
    @classmethod
    def job_list(cls, filters: dict, version: Optional[int] = None) -> str:
        """Cache key for job list with filters."""
        return cls.build_key_from_dict('jobs:list', filters, version=version)
    
    @classmethod
    def job_detail(cls, job_id: int, version: Optional[int] = None) -> str:
        """Cache key for job detail."""
        return cls.build_key('jobs', 'detail', str(job_id), version=version)
    
    @classmethod
    def user_profile(cls, user_id: int, version: Optional[int] = None) -> str:
        """Cache key for user profile."""
        return cls.build_key('users', 'profile', str(user_id), version=version)
    
    @classmethod
    def search_results(cls, query: str, filters: dict, version: Optional[int] = None) -> str:
        """Cache key for search results."""
        search_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return cls.build_key_from_dict(f'search:{search_hash}', filters, version=version)


def cache_result(
    timeout: int = settings.CACHE_TIMEOUT_MEDIUM,
    key_func: Optional[Callable] = None,
    version: Optional[int] = None
):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds
        key_func: Function to generate cache key from function arguments
        version: Cache version for invalidation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name and arguments
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = CacheKeyBuilder.build_key(*key_parts, version=version)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str):
    """
    Invalidate all cache keys matching a pattern.
    Note: This requires Redis and may be slow with many keys.
    
    Args:
        pattern: Cache key pattern (e.g., 'jobboard:jobs:*')
    """
    try:
        from django_redis import get_redis_connection
        redis_client = get_redis_connection('default')
        
        # Find all keys matching pattern
        keys = []
        cursor = 0
        while True:
            cursor, partial_keys = redis_client.scan(cursor, match=pattern, count=100)
            keys.extend(partial_keys)
            if cursor == 0:
                break
        
        # Delete all matching keys
        if keys:
            redis_client.delete(*keys)
            return len(keys)
        return 0
    except Exception:
        # Fallback: clear entire cache if pattern matching fails
        cache.clear()
        return -1


def invalidate_category_cache(category_id: Optional[int] = None):
    """Invalidate category-related cache."""
    if category_id:
        cache.delete(CacheKeyBuilder.category_detail(category_id))
    # Always invalidate list cache when any category changes
    cache.delete(CacheKeyBuilder.category_list())


def invalidate_job_cache(job_id: Optional[int] = None):
    """Invalidate job-related cache."""
    if job_id:
        cache.delete(CacheKeyBuilder.job_detail(job_id))
    # Invalidate featured jobs and list caches
    cache.delete(CacheKeyBuilder.featured_jobs())
    # Invalidate all job list caches (pattern matching)
    invalidate_cache_pattern(f"{CacheKeyBuilder.PREFIX}:jobs:list:*")


def invalidate_user_cache(user_id: Optional[int] = None):
    """Invalidate user-related cache."""
    if user_id:
        cache.delete(CacheKeyBuilder.user_profile(user_id))


def warm_cache():
    """
    Warm up commonly accessed cache entries.
    This can be called on application startup or via a management command.
    """
    from apps.jobs.models import Category, Job
    
    # Warm category list
    categories = list(Category.objects.all().values('id', 'name', 'slug', 'parent_id'))
    cache.set(
        CacheKeyBuilder.category_list(),
        categories,
        settings.CACHE_TIMEOUT_LONG
    )
    
    # Warm featured jobs
    featured_jobs = list(
        Job.objects.filter(is_featured=True, status='active')
        .select_related('category', 'employer')
        .order_by('-created_at')[:10]
        .values('id', 'title', 'category_id', 'employer_id', 'location', 'job_type')
    )
    cache.set(
        CacheKeyBuilder.featured_jobs(),
        featured_jobs,
        settings.CACHE_TIMEOUT_MEDIUM
    )
