"""
Middleware for automatic audit logging.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from apps.core.audit_service import AuditService
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log API requests to audit trail.
    """
    
    # Methods that modify data
    WRITE_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # Paths to exclude from audit logging
    EXCLUDED_PATHS = [
        '/health/',
        '/api/docs/',
        '/api/redoc/',
        '/static/',
        '/media/',
        '/admin/jsi18n/',
    ]
    
    def process_response(self, request, response):
        """Log request/response to audit trail."""
        # Skip excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return response
        
        # Only log write operations
        if request.method not in self.WRITE_METHODS:
            return response
        
        # Only log successful operations
        if response.status_code >= 400:
            return response
        
        try:
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            
            # Get IP address
            ip_address = self._get_client_ip(request)
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Determine action based on method
            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete',
            }
            action = action_map.get(request.method, 'other')
            
            # Build a descriptive object_repr from the request path
            object_repr = f"{request.method} {request.path}"
            
            # Log the action
            AuditService.log_action(
                action=action,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                request_path=request.path,
                request_method=request.method,
                metadata={
                    'status_code': response.status_code,
                    'content_type': response.get('Content-Type', ''),
                    'object_repr': object_repr,
                }
            )
        except Exception as e:
            logger.error(f"Error in audit logging middleware: {e}")
        
        return response
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
