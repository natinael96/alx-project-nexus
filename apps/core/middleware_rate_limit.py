"""
Rate limiting middleware for global API rate limiting.
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from .rate_limit import get_client_identifier, check_rate_limit, RATE_LIMITS
import logging

logger = logging.getLogger(__name__)


class GlobalRateLimitMiddleware:
    """
    Middleware to apply global rate limiting to all API requests.
    
    Applies different rate limits based on:
    - Authentication status (authenticated users get higher limits)
    - Endpoint type (some endpoints have specific limits)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip rate limiting for certain paths
        skip_paths = ['/health/', '/admin/', '/static/', '/media/', '/api/docs/', '/api/redoc/']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)
        
        # Determine rate limit based on authentication
        if hasattr(request, 'user') and request.user.is_authenticated:
            limit = RATE_LIMITS['api_authenticated']['limit']
            period = RATE_LIMITS['api_authenticated']['period']
        else:
            limit = RATE_LIMITS['api_default']['limit']
            period = RATE_LIMITS['api_default']['period']
        
        # Generate rate limit key
        client_id = get_client_identifier(request)
        rate_key = f"api_global:{client_id}"
        
        # Check rate limit
        is_allowed, rate_info = check_rate_limit(rate_key, limit, period)
        
        if not is_allowed:
            logger.warning(
                f"Global rate limit exceeded for {client_id}: {limit} requests per {period}s"
            )
            
            # Return appropriate response
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
        
        # Process request
        response = self.get_response(request)
        
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
