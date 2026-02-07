"""
Rate limiting utilities and decorators.
"""
from functools import wraps
from typing import Optional, Callable
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
import hashlib
import logging

logger = logging.getLogger(__name__)


def get_cache_ttl(cache_key: str, fallback: int) -> int:
    """
    Get the TTL (time to live) for a cache key.
    Works with both django-redis and Django's built-in cache backends.
    
    Args:
        cache_key: The cache key to check
        fallback: Fallback TTL value if TTL cannot be determined
        
    Returns:
        TTL in seconds, or fallback value if TTL method is not available
    """
    # Check if cache backend supports ttl() method (django-redis)
    if hasattr(cache, 'ttl'):
        try:
            ttl = cache.ttl(cache_key)
            if ttl is not None and ttl > 0:
                return ttl
        except (AttributeError, TypeError):
            # ttl() method exists but may not work with this backend
            pass
    
    # Fallback: return the provided fallback value
    return fallback


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


def get_client_identifier(request):
    """
    Get a unique identifier for the client making the request.
    Uses authenticated user ID if available, otherwise IP address.
    
    Args:
        request: Django request object
        
    Returns:
        String identifier for the client
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        return f"user:{request.user.id}"
    
    # Get IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    
    return f"ip:{ip}"


def check_rate_limit(
    key: str,
    limit: int,
    period: int,
    increment: bool = True
) -> tuple[bool, dict]:
    """
    Check if a rate limit has been exceeded.
    
    Args:
        key: Cache key for rate limiting
        limit: Maximum number of requests allowed
        period: Time period in seconds
        increment: Whether to increment the counter
        
    Returns:
        Tuple of (is_allowed, rate_limit_info)
    """
    cache_key = f"ratelimit:{key}"
    
    # Get current count
    current_count = cache.get(cache_key, 0)
    
    # Check if limit exceeded
    if current_count >= limit:
        # Get TTL to calculate reset time
        ttl = get_cache_ttl(cache_key, period)
        
        return False, {
            'limit': limit,
            'remaining': 0,
            'reset': int(timezone.now().timestamp()) + ttl,
            'retry_after': ttl,
        }
    
    # Increment counter if requested
    if increment:
        cache.set(cache_key, current_count + 1, period)
    
    # Calculate remaining requests
    remaining = max(0, limit - current_count - (1 if increment else 0))
    
    # Get TTL for reset time
    ttl = get_cache_ttl(cache_key, period)
    
    return True, {
        'limit': limit,
        'remaining': remaining,
        'reset': int(timezone.now().timestamp()) + ttl,
    }


def rate_limit(
    limit: int,
    period: int,
    key_func: Optional[Callable] = None,
    scope: str = 'default',
    method: Optional[str] = None
):
    """
    Decorator to rate limit a view function.
    
    Args:
        limit: Maximum number of requests allowed
        period: Time period in seconds
        key_func: Function to generate rate limit key (default: uses client identifier)
        scope: Scope identifier for the rate limit
        method: HTTP method to apply rate limit to (None = all methods)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if method matches
            if method and request.method != method:
                return view_func(request, *args, **kwargs)
            
            # Generate rate limit key
            if key_func:
                rate_key = key_func(request, *args, **kwargs)
            else:
                client_id = get_client_identifier(request)
                rate_key = f"{scope}:{client_id}"
            
            # Check rate limit
            is_allowed, rate_info = check_rate_limit(rate_key, limit, period)
            
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded for {rate_key}: {rate_info['limit']} requests per {period}s"
                )
                
                # Return appropriate response based on view type
                if hasattr(request, 'accepted_renderer'):
                    # DRF view
                    response = Response(
                        {
                            'error': 'Rate limit exceeded',
                            'detail': f'You have exceeded the rate limit of {limit} requests per {period} seconds.',
                            'retry_after': rate_info['retry_after'],
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                else:
                    # Django view
                    response = JsonResponse(
                        {
                            'error': 'Rate limit exceeded',
                            'detail': f'You have exceeded the rate limit of {limit} requests per {period} seconds.',
                            'retry_after': rate_info['retry_after'],
                        },
                        status=429
                    )
                
                # Add rate limit headers
                response['X-RateLimit-Limit'] = str(rate_info['limit'])
                response['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response['X-RateLimit-Reset'] = str(rate_info['reset'])
                response['Retry-After'] = str(rate_info['retry_after'])
                
                return response
            
            # Call the view function
            response = view_func(request, *args, **kwargs)
            
            # Add rate limit headers to successful responses
            if hasattr(response, 'data'):
                # DRF response
                response['X-RateLimit-Limit'] = str(rate_info['limit'])
                response['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response['X-RateLimit-Reset'] = str(rate_info['reset'])
            elif hasattr(response, 'headers'):
                # Django response
                response['X-RateLimit-Limit'] = str(rate_info['limit'])
                response['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response['X-RateLimit-Reset'] = str(rate_info['reset'])
            
            return response
        
        return wrapper
    return decorator


# Predefined rate limit configurations
RATE_LIMITS = {
    'login': {'limit': 5, 'period': 300},  # 5 attempts per 5 minutes
    'register': {'limit': 3, 'period': 3600},  # 3 registrations per hour
    'job_create': {'limit': 10, 'period': 3600},  # 10 jobs per hour
    'application_submit': {'limit': 20, 'period': 3600},  # 20 applications per hour
    'search': {'limit': 60, 'period': 60},  # 60 searches per minute
    'api_default': {'limit': 100, 'period': 60},  # 100 requests per minute
    'api_authenticated': {'limit': 200, 'period': 60},  # 200 requests per minute for authenticated users
}


def rate_limit_login(request, *args, **kwargs):
    """Rate limit key function for login attempts."""
    client_id = get_client_identifier(request)
    return f"login:{client_id}"


def rate_limit_register(request, *args, **kwargs):
    """Rate limit key function for registration."""
    # Use IP address for registration (before user is created)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return f"register:ip:{ip}"


def rate_limit_job_create(request, *args, **kwargs):
    """Rate limit key function for job creation."""
    if hasattr(request, 'user') and request.user.is_authenticated:
        return f"job_create:user:{request.user.id}"
    return f"job_create:{get_client_identifier(request)}"


def rate_limit_application_submit(request, *args, **kwargs):
    """Rate limit key function for application submission."""
    if hasattr(request, 'user') and request.user.is_authenticated:
        return f"application_submit:user:{request.user.id}"
    return f"application_submit:{get_client_identifier(request)}"


def rate_limit_search(request, *args, **kwargs):
    """Rate limit key function for search."""
    client_id = get_client_identifier(request)
    return f"search:{client_id}"
