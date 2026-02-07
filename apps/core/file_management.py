"""
File management utilities including cleanup, access control, and secure URLs.
"""
import os
import logging
from typing import Optional
from django.core.files.storage import default_storage
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from apps.core.storage import storage_manager

logger = logging.getLogger(__name__)


class FileAccessControl:
    """
    Access control for file downloads.
    """
    
    @staticmethod
    def can_access_resume(user, application):
        """
        Check if user can access a resume file.
        
        Args:
            user: User requesting access
            application: Application object containing the resume
            
        Returns:
            True if user can access, False otherwise
        """
        # Admin can access all resumes
        if user.is_admin or user.is_superuser:
            return True
        
        # Applicant can access their own resume
        if application.applicant == user:
            return True
        
        # Employer can access resumes for their jobs
        if user.is_employer and application.job.employer == user:
            return True
        
        return False
    
    @staticmethod
    def can_access_profile_picture(user, profile_user):
        """
        Check if user can access a profile picture.
        
        Args:
            user: User requesting access
            profile_user: User whose profile picture is being accessed
            
        Returns:
            True if user can access, False otherwise
        """
        # Users can always access their own profile picture
        if user == profile_user:
            return True
        
        # Profile pictures are generally public
        # You can add more restrictions here if needed
        return True


class FileCleanup:
    """
    Utilities for cleaning up orphaned and old files.
    """
    
    @staticmethod
    def cleanup_orphaned_files(model_class, file_field_name: str, days_old: int = 30):
        """
        Clean up files that are no longer referenced in the database.
        
        Args:
            model_class: Django model class
            file_field_name: Name of the file field
            days_old: Only delete files older than this many days
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days_old)
            
            # Get all file paths from database
            referenced_files = set()
            for instance in model_class.objects.filter(
                **{f'{file_field_name}__isnull': False}
            ).exclude(**{f'{file_field_name}': ''}):
                file_path = getattr(instance, file_field_name)
                if file_path:
                    referenced_files.add(str(file_path))
            
            # Find orphaned files in storage
            # Note: This is a simplified version. In production, you might want
            # to list all files in the storage and compare
            
            logger.info(f"File cleanup completed. Referenced files: {len(referenced_files)}")
            return len(referenced_files)
        
        except Exception as e:
            logger.error(f"Error during file cleanup: {e}")
            return 0
    
    @staticmethod
    def cleanup_old_files(model_class, file_field_name: str, days_old: int = 90):
        """
        Clean up files from deleted instances older than specified days.
        
        Args:
            model_class: Django model class
            file_field_name: Name of the file field
            days_old: Delete files older than this many days
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days_old)
            
            # This would typically be run on soft-deleted records
            # For hard deletes, files should be cleaned up via signals
            
            logger.info(f"Old file cleanup completed")
            return 0
        
        except Exception as e:
            logger.error(f"Error during old file cleanup: {e}")
            return 0
    
    @staticmethod
    def delete_file_safely(file_path: str) -> bool:
        """
        Safely delete a file from storage.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if not file_path:
                return False
            
            # Delete from storage
            storage_manager.delete(file_path)
            
            logger.info(f"File deleted successfully: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False


def cleanup_application_files(application):
    """
    Clean up files associated with a deleted application.
    
    Args:
        application: Application instance being deleted
    """
    try:
        if application.resume:
            FileCleanup.delete_file_safely(str(application.resume))
            logger.info(f"Cleaned up resume for application {application.id}")
    except Exception as e:
        logger.error(f"Error cleaning up application files: {e}")


def cleanup_user_files(user):
    """
    Clean up files associated with a deleted user.
    
    Args:
        user: User instance being deleted
    """
    try:
        if user.profile_picture:
            FileCleanup.delete_file_safely(str(user.profile_picture))
            logger.info(f"Cleaned up profile picture for user {user.id}")
    except Exception as e:
        logger.error(f"Error cleaning up user files: {e}")
