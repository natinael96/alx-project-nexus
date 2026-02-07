"""
Custom middleware for logging and monitoring.
"""
import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from django.db.backends.utils import CursorWrapper

logger = logging.getLogger('apps.api')
performance_logger = logging.getLogger('apps.performance')


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests and responses.
    
    Logs:
    - Request method, path, and query parameters
    - Response status code
    - Request duration
    - User information (if authenticated)
    """
    
    def process_request(self, request):
        """Store request start time."""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log API request and response."""
        # Skip logging for certain paths
        skip_paths = ['/health/', '/admin/', '/static/', '/media/', '/api/docs/', '/api/redoc/']
        if any(request.path.startswith(path) for path in skip_paths):
            return response
        
        # Calculate request duration
        duration = time.time() - getattr(request, '_start_time', time.time())
        
        # Prepare log data
        log_data = {
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user': None,
            'ip_address': self.get_client_ip(request),
        }
        
        # Add user information if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            log_data['user'] = {
                'id': request.user.id,
                'username': request.user.username,
                'role': request.user.role,
            }
        
        # Log based on status code
        if response.status_code >= 500:
            logger.error('API Request', extra=log_data)
        elif response.status_code >= 400:
            logger.warning('API Request', extra=log_data)
        else:
            logger.info('API Request', extra=log_data)
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor and log performance metrics.
    
    Tracks:
    - Request duration
    - Database query count and time
    - Slow requests (> 1 second)
    """
    
    def process_request(self, request):
        """Initialize performance tracking."""
        request._perf_start_time = time.time()
        request._perf_query_count = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """Log performance metrics."""
        # Skip logging for certain paths
        skip_paths = ['/health/', '/admin/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return response
        
        duration = time.time() - getattr(request, '_perf_start_time', time.time())
        query_count = len(connection.queries) - getattr(request, '_perf_query_count', 0)
        
        # Calculate total query time
        query_time = sum(float(q['time']) for q in connection.queries[-query_count:]) if query_count > 0 else 0
        
        perf_data = {
            'path': request.path,
            'method': request.method,
            'duration_ms': round(duration * 1000, 2),
            'query_count': query_count,
            'query_time_ms': round(query_time * 1000, 2),
            'slow_request': duration > 1.0,
        }
        
        # Log slow requests as warnings
        if duration > 1.0:
            performance_logger.warning('Slow Request Detected', extra=perf_data)
        else:
            performance_logger.info('Request Performance', extra=perf_data)
        
        return response


class DatabaseQueryLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log database queries for debugging.
    Only active when DEBUG=True or DB_LOG_LEVEL=DEBUG.
    """
    
    def process_response(self, request, response):
        """Log database queries if enabled."""
        from django.conf import settings
        
        # Only log in debug mode or if explicitly enabled
        if not (settings.DEBUG or settings.LOGGING['loggers']['django.db.backends']['level'] == 'DEBUG'):
            return response
        
        # Skip logging for certain paths
        skip_paths = ['/health/', '/admin/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return response
        
        query_count = len(connection.queries)
        if query_count > 0:
            total_time = sum(float(q['time']) for q in connection.queries)
            
            db_logger = logging.getLogger('django.db.backends')
            db_logger.debug(
                f'Database queries: {query_count} queries in {total_time:.3f}s',
                extra={
                    'query_count': query_count,
                    'total_time': total_time,
                    'path': request.path,
                }
            )
        
        return response
