"""
Health check utilities and views.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available. System resource monitoring will be limited.")


def check_database():
    """Check database connectivity."""
    try:
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        response_time = (time.time() - start_time) * 1000
        return {'status': 'healthy', 'response_time_ms': round(response_time, 2)}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}


def check_cache():
    """Check cache connectivity."""
    try:
        start_time = time.time()
        cache.set('health_check', 'ok', 5)
        value = cache.get('health_check')
        response_time = (time.time() - start_time) * 1000
        
        if value == 'ok':
            return {'status': 'healthy', 'response_time_ms': round(response_time, 2)}
        else:
            return {'status': 'unhealthy', 'error': 'Cache read/write failed'}
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}


def check_disk_space():
    """Check available disk space."""
    if not PSUTIL_AVAILABLE:
        return {'status': 'unknown', 'message': 'psutil not available'}
    
    try:
        disk = psutil.disk_usage('/')
        total_gb = disk.total / (1024 ** 3)
        used_gb = disk.used / (1024 ** 3)
        free_gb = disk.free / (1024 ** 3)
        percent_used = (disk.used / disk.total) * 100
        
        status = 'healthy'
        if percent_used > 90:
            status = 'warning'
        elif percent_used > 95:
            status = 'critical'
        
        return {
            'status': status,
            'total_gb': round(total_gb, 2),
            'used_gb': round(used_gb, 2),
            'free_gb': round(free_gb, 2),
            'percent_used': round(percent_used, 2),
        }
    except Exception as e:
        logger.error(f"Disk space check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}


def check_memory():
    """Check system memory usage."""
    if not PSUTIL_AVAILABLE:
        return {'status': 'unknown', 'message': 'psutil not available'}
    
    try:
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024 ** 3)
        used_gb = memory.used / (1024 ** 3)
        available_gb = memory.available / (1024 ** 3)
        percent_used = memory.percent
        
        status = 'healthy'
        if percent_used > 85:
            status = 'warning'
        elif percent_used > 95:
            status = 'critical'
        
        return {
            'status': status,
            'total_gb': round(total_gb, 2),
            'used_gb': round(used_gb, 2),
            'available_gb': round(available_gb, 2),
            'percent_used': round(percent_used, 2),
        }
    except Exception as e:
        logger.error(f"Memory check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}


def health_check(request):
    """
    Comprehensive health check endpoint.
    
    Returns:
    - 200: All checks passed
    - 503: One or more checks failed
    """
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'disk': check_disk_space(),
        'memory': check_memory(),
    }
    
    # Determine overall status
    overall_status = 'healthy'
    status_code = 200
    
    for check_name, check_result in checks.items():
        if check_result.get('status') == 'unhealthy':
            overall_status = 'unhealthy'
            status_code = 503
            break
        elif check_result.get('status') == 'warning' and overall_status == 'healthy':
            overall_status = 'degraded'
            status_code = 200  # Still return 200 but indicate degraded
    
    response_data = {
        'status': overall_status,
        'timestamp': time.time(),
        'checks': checks,
    }
    
    return JsonResponse(response_data, status=status_code)


def liveness_check(request):
    """
    Simple liveness check endpoint.
    Returns 200 if the application is running.
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': time.time(),
    })


def readiness_check(request):
    """
    Readiness check endpoint.
    Returns 200 if the application is ready to serve traffic.
    """
    db_check = check_database()
    
    if db_check['status'] == 'healthy':
        return JsonResponse({
            'status': 'ready',
            'timestamp': time.time(),
        })
    else:
        return JsonResponse({
            'status': 'not_ready',
            'error': 'Database connection failed',
            'timestamp': time.time(),
        }, status=503)
