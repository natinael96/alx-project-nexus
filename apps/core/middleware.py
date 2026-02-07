"""
Custom middleware for logging and monitoring.
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.db import connection

logger = logging.getLogger('apps.api')
performance_logger = logging.getLogger('apps.performance')


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests and responses.
    """

    def process_request(self, request):
        """Store request start time."""
        request._start_time = time.time()
        return None

    def process_response(self, request, response):
        """Log API request and response."""
        skip_paths = ['/health/', '/admin/', '/static/', '/media/', '/api/docs/', '/api/redoc/']
        if any(request.path.startswith(path) for path in skip_paths):
            return response

        duration = time.time() - getattr(request, '_start_time', time.time())
        duration_ms = round(duration * 1000, 2)
        status = response.status_code
        method = request.method
        path = request.path
        ip = self.get_client_ip(request)
        query_params = dict(request.GET)

        # Build user string
        user_str = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_str = f'{request.user.username} (id={request.user.id}, role={getattr(request.user, "role", "N/A")})'

        # Build query string
        qs = f' ?{query_params}' if query_params else ''

        msg = f'{method} {path}{qs} -> {status} | {duration_ms}ms | user={user_str} | ip={ip}'

        if status >= 500:
            logger.error(msg)
        elif status >= 400:
            logger.warning(msg)
        else:
            logger.info(msg)

        return response

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor and log performance metrics.
    Flags slow requests (> 1 second).
    """

    def process_request(self, request):
        """Initialize performance tracking."""
        request._perf_start_time = time.time()
        request._perf_query_count = len(connection.queries)
        return None

    def process_response(self, request, response):
        """Log performance metrics."""
        skip_paths = ['/health/', '/admin/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return response

        duration = time.time() - getattr(request, '_perf_start_time', time.time())
        duration_ms = round(duration * 1000, 2)
        query_count = len(connection.queries) - getattr(request, '_perf_query_count', 0)

        # Calculate total query time
        query_time = 0
        if query_count > 0:
            query_time = sum(float(q['time']) for q in connection.queries[-query_count:])
        query_time_ms = round(query_time * 1000, 2)

        method = request.method
        path = request.path

        if duration > 1.0:
            performance_logger.warning(
                f'SLOW REQUEST: {method} {path} | {duration_ms}ms total | '
                f'{query_count} queries in {query_time_ms}ms | '
                f'threshold=1000ms exceeded by {round(duration_ms - 1000, 2)}ms'
            )
        elif duration > 0.5:
            performance_logger.info(
                f'MODERATE REQUEST: {method} {path} | {duration_ms}ms total | '
                f'{query_count} queries in {query_time_ms}ms'
            )

        return response


class DatabaseQueryLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log database queries for debugging.
    Only active when DEBUG=True or DB_LOG_LEVEL=DEBUG.
    """

    def process_response(self, request, response):
        """Log database queries if enabled."""
        from django.conf import settings

        if not (settings.DEBUG or settings.LOGGING['loggers']['django.db.backends']['level'] == 'DEBUG'):
            return response

        skip_paths = ['/health/', '/admin/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return response

        query_count = len(connection.queries)
        if query_count > 0:
            total_time = sum(float(q['time']) for q in connection.queries)

            db_logger = logging.getLogger('django.db.backends')
            db_logger.debug(
                f'{request.method} {request.path} | '
                f'{query_count} DB queries in {total_time:.3f}s'
            )

        return response
