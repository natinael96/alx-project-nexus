"""
Audit service for logging system actions and changes.
"""
import logging
from typing import Optional, Dict, Any
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from apps.core.models_audit import AuditLog, ChangeHistory
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for creating audit logs and tracking changes.
    """
    
    @staticmethod
    def log_action(
        action: str,
        user: Optional[User] = None,
        obj: Optional[Any] = None,
        changes: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_path: Optional[str] = None,
        request_method: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> AuditLog:
        """
        Log an action to the audit trail.
        
        Args:
            action: Action type (create, update, delete, etc.)
            user: User who performed the action
            obj: Object affected (optional)
            changes: Dictionary of changes {field: {old: value, new: value}}
            ip_address: IP address of the user
            user_agent: User agent string
            request_path: API endpoint or URL
            request_method: HTTP method
            metadata: Additional metadata
            
        Returns:
            Created AuditLog instance
        """
        try:
            content_type = None
            object_id = None
            object_repr = str(obj) if obj else ''
            
            if obj:
                content_type = ContentType.objects.get_for_model(obj)
                object_id = obj.pk
            
            # Fallback: use request info if no object_repr
            if not object_repr and request_method and request_path:
                object_repr = f"{request_method} {request_path}"
            
            audit_log = AuditLog.objects.create(
                user=user,
                action=action,
                content_type=content_type,
                object_id=object_id,
                object_repr=object_repr,
                changes=changes or {},
                ip_address=ip_address,
                user_agent=user_agent or '',
                request_path=request_path or '',
                request_method=request_method or '',
                metadata=metadata or {}
            )
            
            return audit_log
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            return None
    
    @staticmethod
    def log_change(
        obj: Any,
        field_name: str,
        old_value: Any,
        new_value: Any,
        changed_by: Optional[User] = None,
        change_reason: Optional[str] = None
    ) -> ChangeHistory:
        """
        Log a specific field change.
        
        Args:
            obj: Object that changed
            field_name: Name of the field
            old_value: Old value
            new_value: New value
            changed_by: User who made the change
            change_reason: Reason for the change
            
        Returns:
            Created ChangeHistory instance
        """
        try:
            content_type = ContentType.objects.get_for_model(obj)
            
            # Serialize values
            old_val_str = str(old_value) if old_value is not None else ''
            new_val_str = str(new_value) if new_value is not None else ''
            
            change_history = ChangeHistory.objects.create(
                content_type=content_type,
                object_id=obj.pk,
                changed_by=changed_by,
                field_name=field_name,
                old_value=old_val_str,
                new_value=new_val_str,
                change_reason=change_reason or ''
            )
            
            return change_history
        except Exception as e:
            logger.error(f"Error creating change history: {e}")
            return None
    
    @staticmethod
    def get_object_history(obj: Any, limit: int = 50) -> list:
        """
        Get change history for a specific object.
        
        Args:
            obj: Object to get history for
            limit: Maximum number of history items
            
        Returns:
            List of ChangeHistory instances
        """
        try:
            content_type = ContentType.objects.get_for_model(obj)
            return ChangeHistory.objects.filter(
                content_type=content_type,
                object_id=obj.pk
            ).order_by('-created_at')[:limit]
        except Exception as e:
            logger.error(f"Error getting object history: {e}")
            return []
    
    @staticmethod
    def get_user_audit_logs(user: User, limit: int = 100) -> list:
        """
        Get audit logs for a specific user.
        
        Args:
            user: User to get logs for
            limit: Maximum number of logs
            
        Returns:
            List of AuditLog instances
        """
        return AuditLog.objects.filter(
            user=user
        ).order_by('-created_at')[:limit]
