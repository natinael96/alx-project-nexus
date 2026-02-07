"""
Performance optimization middleware.
"""
import gzip
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)


class CompressionMiddleware(MiddlewareMixin):
    """
    Middleware to compress API responses.
    """
    
    def process_response(self, request, response):
        """Compress response if client supports it."""
        # Only compress for API endpoints
        if not request.path.startswith('/api/'):
            return response
        
        # Check if client accepts gzip
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' not in accept_encoding:
            return response
        
        # Don't compress if already compressed
        if response.get('Content-Encoding', ''):
            return response
        
        # Don't compress small responses
        content_length = len(response.content)
        if content_length < 200:  # Less than 200 bytes
            return response
        
        # Compress the content
        try:
            compressed_content = gzip.compress(response.content)
            response.content = compressed_content
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = str(len(compressed_content))
            logger.debug(f"Compressed response: {content_length} -> {len(compressed_content)} bytes")
        except Exception as e:
            logger.error(f"Error compressing response: {e}")
        
        return response
