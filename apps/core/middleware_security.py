"""
Security middleware for IP whitelisting and API key authentication.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from apps.core.security_service import SecurityService
from apps.core.models_security import APIKey
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Middleware to enforce IP whitelisting for admin access.
    """
    
    # Paths that require IP whitelisting
    PROTECTED_PATHS = [
        '/admin/',
        '/api/auth/users/',  # Admin user management
    ]
    
    def process_request(self, request):
        """Check if IP is whitelisted for protected paths."""
        # Only check for protected paths
        if not any(request.path.startswith(path) for path in self.PROTECTED_PATHS):
            return None
        
        # Skip if IP whitelisting is disabled
        if not getattr(settings, 'ENABLE_IP_WHITELIST', False):
            return None
        
        # Get client IP
        ip_address = self._get_client_ip(request)
        
        # Check if user is admin
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'is_admin') and request.user.is_admin:
                # Check IP whitelist
                if not SecurityService.is_ip_whitelisted(ip_address):
                    logger.warning(f"Admin access denied for IP: {ip_address}")
                    SecurityService.log_security_event(
                        'unauthorized_access',
                        user=request.user,
                        ip_address=ip_address,
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        details={'path': request.path, 'reason': 'ip_not_whitelisted'}
                    )
                    
                    # Return appropriate response
                    try:
                        from rest_framework.response import Response
                        from rest_framework import status
                        if hasattr(request, 'accepted_renderer'):
                            # DRF request
                            return Response(
                                {'error': 'Access denied. Your IP address is not whitelisted.'},
                                status=status.HTTP_403_FORBIDDEN
                            )
                    except ImportError:
                        pass
                    
                    # Django request
                    return JsonResponse(
                        {'error': 'Access denied. Your IP address is not whitelisted.'},
                        status=403
                    )
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIKeyAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware for API key authentication (alternative to JWT).
    """
    
    def process_request(self, request):
        """Authenticate using API key if provided."""
        # Check for API key in header
        api_key = request.META.get('HTTP_X_API_KEY') or request.META.get('HTTP_AUTHORIZATION', '').replace('ApiKey ', '')
        
        if not api_key:
            return None
        
        # Get client IP
        ip_address = self._get_client_ip(request)
        
        # Validate API key
        api_key_obj = SecurityService.validate_api_key(api_key, ip_address)
        
        if api_key_obj:
            # Set user on request
            request.user = api_key_obj.user
            request.api_key = api_key_obj
            logger.debug(f"API key authentication successful for user: {api_key_obj.user.username}")
        else:
            logger.warning(f"Invalid API key attempt from IP: {ip_address}")
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
