"""
Utility functions for the application.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


def validate_file_size(file, max_size_mb=5):
    """
    Validate that uploaded file size is within limit.
    
    Args:
        file: Uploaded file object
        max_size_mb: Maximum file size in MB (default: 5MB)
    
    Raises:
        ValidationError: If file size exceeds limit
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(
            f'File size cannot exceed {max_size_mb}MB. '
            f'Current file size: {file.size / (1024 * 1024):.2f}MB'
        )


def validate_file_extension(file, allowed_extensions):
    """
    Validate that uploaded file has allowed extension.
    
    Args:
        file: Uploaded file object
        allowed_extensions: List of allowed file extensions (e.g., ['pdf', 'doc', 'docx'])
    
    Raises:
        ValidationError: If file extension is not allowed
    """
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        raise ValidationError(
            f'File extension "{file_extension}" is not allowed. '
            f'Allowed extensions: {", ".join(allowed_extensions)}'
        )


def get_recent_date(days=30):
    """
    Get a date that is N days ago from now.
    
    Args:
        days: Number of days ago (default: 30)
    
    Returns:
        datetime: Date N days ago
    """
    return timezone.now() - timedelta(days=days)

