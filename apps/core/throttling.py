"""
Custom throttling classes for API rate limiting.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from django.core.cache import cache
from django.conf import settings
import time


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle that allows burst requests but limits sustained rate.
    """
    scope = 'burst'
    
    def get_cache_key(self, request, view):
        """Generate cache key for burst throttling."""
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class UserBurstRateThrottle(UserRateThrottle):
    """
    User-based burst rate throttle.
    Allows short bursts but limits overall rate.
    """
    scope = 'user_burst'
    
    def allow_request(self, request, view):
        """
        Implement the throttling logic.
        Allows burst of requests but limits sustained rate.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            return True  # Let AnonRateThrottle handle anonymous users
        
        # Get rate limits from settings
        num_requests = getattr(settings, 'REST_FRAMEWORK', {}).get(
            'DEFAULT_THROTTLE_RATES', {}
        ).get(self.scope, '100/hour').split('/')[0]
        
        duration = 60  # 1 minute window for burst
        
        cache_key = self.get_cache_key(request, view)
        history = cache.get(cache_key, [])
        now = time.time()
        
        # Remove old entries
        history = [h for h in history if h > now - duration]
        
        if len(history) >= int(num_requests):
            return False
        
        history.append(now)
        cache.set(cache_key, history, duration)
        return True


class AnonBurstRateThrottle(AnonRateThrottle):
    """
    Anonymous user burst rate throttle.
    """
    scope = 'anon_burst'
    
    def allow_request(self, request, view):
        """Implement burst throttling for anonymous users."""
        if request.user.is_authenticated:
            return True  # Let UserRateThrottle handle authenticated users
        
        ident = self.get_ident(request)
        num_requests = 20  # Lower limit for anonymous
        duration = 60  # 1 minute
        
        cache_key = self.get_cache_key(request, view)
        history = cache.get(cache_key, [])
        now = time.time()
        
        history = [h for h in history if h > now - duration]
        
        if len(history) >= num_requests:
            return False
        
        history.append(now)
        cache.set(cache_key, history, duration)
        return True


class ReadWriteThrottle(ScopedRateThrottle):
    """
    Scope-based throttle that differentiates between read and write operations.
    """
    def get_scope(self, request, view):
        """Determine scope based on HTTP method."""
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return 'read'
        elif request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return 'write'
        return 'default'


class IPBasedThrottle(AnonRateThrottle):
    """
    IP-based rate throttle for anonymous users.
    """
    scope = 'ip_based'
    
    def get_ident(self, request):
        """Use IP address as identifier."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
