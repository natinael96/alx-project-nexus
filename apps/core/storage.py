"""
File storage abstraction layer with support for multiple backends.
Supports Supabase Storage and local filesystem.
"""
import os
import logging
from django.core.files.storage import Storage, default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible
from typing import Optional, BinaryIO
import hashlib
from datetime import timedelta
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@deconstructible
class StorageBackend:
    """
    Abstract storage backend interface.
    """
    
    def save(self, name: str, content: BinaryIO, max_length: Optional[int] = None) -> str:
        """Save a file and return its name."""
        raise NotImplementedError
    
    def delete(self, name: str) -> None:
        """Delete a file."""
        raise NotImplementedError
    
    def exists(self, name: str) -> bool:
        """Check if a file exists."""
        raise NotImplementedError
    
    def url(self, name: str) -> str:
        """Return the URL of a file."""
        raise NotImplementedError
    
    def size(self, name: str) -> int:
        """Return the size of a file."""
        raise NotImplementedError
    
    def generate_signed_url(self, name: str, expiration: int = 3600) -> str:
        """Generate a signed URL for secure file access."""
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    """
    Local filesystem storage backend (default Django storage).
    """
    
    def __init__(self):
        self.storage = default_storage
    
    def save(self, name: str, content: BinaryIO, max_length: Optional[int] = None) -> str:
        return self.storage.save(name, content)
    
    def delete(self, name: str) -> None:
        if self.exists(name):
            self.storage.delete(name)
    
    def exists(self, name: str) -> bool:
        return self.storage.exists(name)
    
    def url(self, name: str) -> str:
        return self.storage.url(name)
    
    def size(self, name: str) -> int:
        return self.storage.size(name)
    
    def generate_signed_url(self, name: str, expiration: int = 3600) -> str:
        # Local storage doesn't need signed URLs, return regular URL
        return self.url(name)


class SupabaseStorageBackend(StorageBackend):
    """
    Supabase Storage backend for cloud file storage.
    """
    
    def __init__(self, bucket_name: str = None):
        try:
            from supabase import create_client, Client
            self.bucket_name = bucket_name or getattr(settings, 'SUPABASE_STORAGE_BUCKET', 'files')
            self.supabase_url = getattr(settings, 'SUPABASE_URL', None)
            self.supabase_key = getattr(settings, 'SUPABASE_KEY', None)
            
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
        except ImportError:
            logger.error("supabase package not installed. Install with: pip install supabase")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def save(self, name: str, content: BinaryIO, max_length: Optional[int] = None) -> str:
        """Save file to Supabase Storage."""
        try:
            # Read content
            if hasattr(content, 'read'):
                file_content = content.read()
            else:
                file_content = content
            
            # Upload to Supabase
            response = self.client.storage.from_(self.bucket_name).upload(
                path=name,
                file=file_content,
                file_options={"content-type": self._get_content_type(name)}
            )
            
            if response:
                return name
            else:
                raise Exception("Failed to upload file to Supabase")
        except Exception as e:
            logger.error(f"Error saving file to Supabase: {e}")
            raise
    
    def delete(self, name: str) -> None:
        """Delete file from Supabase Storage."""
        try:
            self.client.storage.from_(self.bucket_name).remove([name])
        except Exception as e:
            logger.error(f"Error deleting file from Supabase: {e}")
            raise
    
    def exists(self, name: str) -> bool:
        """Check if file exists in Supabase Storage."""
        try:
            files = self.client.storage.from_(self.bucket_name).list(name)
            return any(f['name'] == os.path.basename(name) for f in files)
        except Exception:
            return False
    
    def url(self, name: str) -> str:
        """Get public URL for file."""
        try:
            response = self.client.storage.from_(self.bucket_name).get_public_url(name)
            return response
        except Exception as e:
            logger.error(f"Error getting public URL from Supabase: {e}")
            return ""
    
    def size(self, name: str) -> int:
        """Get file size from Supabase."""
        try:
            files = self.client.storage.from_(self.bucket_name).list(name)
            for f in files:
                if f['name'] == os.path.basename(name):
                    return f.get('metadata', {}).get('size', 0)
            return 0
        except Exception:
            return 0
    
    def generate_signed_url(self, name: str, expiration: int = 3600) -> str:
        """Generate signed URL for secure file access."""
        try:
            response = self.client.storage.from_(self.bucket_name).create_signed_url(
                path=name,
                expires_in=expiration
            )
            return response.get('signedURL', '')
        except Exception as e:
            logger.error(f"Error generating signed URL from Supabase: {e}")
            return ""
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename."""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
        }
        return content_types.get(ext, 'application/octet-stream')


class StorageManager:
    """
    Storage manager that provides a unified interface for multiple storage backends.
    """
    
    _instance = None
    _backend = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._backend is None:
            self._backend = self._get_backend()
    
    def _get_backend(self) -> StorageBackend:
        """Get the configured storage backend."""
        storage_type = getattr(settings, 'FILE_STORAGE_BACKEND', 'local').lower()
        
        if storage_type == 'supabase':
            try:
                return SupabaseStorageBackend(
                    bucket_name=getattr(settings, 'SUPABASE_STORAGE_BUCKET', 'files')
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase storage, falling back to local: {e}")
                return LocalStorageBackend()
        
        else:
            return LocalStorageBackend()
    
    def save(self, name: str, content: BinaryIO, max_length: Optional[int] = None) -> str:
        """Save a file using the configured backend."""
        return self._backend.save(name, content, max_length)
    
    def delete(self, name: str) -> None:
        """Delete a file using the configured backend."""
        return self._backend.delete(name)
    
    def exists(self, name: str) -> bool:
        """Check if a file exists using the configured backend."""
        return self._backend.exists(name)
    
    def url(self, name: str) -> str:
        """Get the URL of a file using the configured backend."""
        return self._backend.url(name)
    
    def size(self, name: str) -> int:
        """Get the size of a file using the configured backend."""
        return self._backend.size(name)
    
    def generate_signed_url(self, name: str, expiration: int = 3600) -> str:
        """Generate a signed URL for secure file access."""
        return self._backend.generate_signed_url(name, expiration)
    
    @property
    def backend(self) -> StorageBackend:
        """Get the current storage backend."""
        return self._backend


# Global storage manager instance
storage_manager = StorageManager()
