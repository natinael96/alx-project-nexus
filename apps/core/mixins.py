"""
Mixins for common model functionality.
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from apps.core.audit_service import AuditService
from apps.core.models_audit import ChangeHistory


class AuditMixin(models.Model):
    """
    Mixin to add automatic audit logging to models.
    """
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Override save to track changes."""
        # Track changes if updating
        if self.pk:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                changes = {}
                
                # Compare fields
                for field in self._meta.fields:
                    if field.name in ['id', 'created_at', 'updated_at']:
                        continue
                    
                    old_value = getattr(old_instance, field.name, None)
                    new_value = getattr(self, field.name, None)
                    
                    if old_value != new_value:
                        changes[field.name] = {
                            'old': str(old_value) if old_value is not None else None,
                            'new': str(new_value) if new_value is not None else None
                        }
                        
                        # Create detailed change history
                        try:
                            changed_by = getattr(self, '_changed_by', None)
                            ChangeHistory.objects.create(
                                content_type=ContentType.objects.get_for_model(self),
                                object_id=self.pk,
                                changed_by=changed_by,
                                field_name=field.name,
                                old_value=str(old_value) if old_value is not None else '',
                                new_value=str(new_value) if new_value is not None else '',
                                change_reason=getattr(self, '_change_reason', '')
                            )
                        except Exception as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Error creating change history: {e}")
                
                # Log audit if there are changes
                if changes:
                    try:
                        changed_by = getattr(self, '_changed_by', None)
                        AuditService.log_action(
                            action='update',
                            user=changed_by,
                            obj=self,
                            changes=changes
                        )
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error creating audit log: {e}")
            except self.__class__.DoesNotExist:
                pass  # New instance
        
        # Call parent save
        super().save(*args, **kwargs)
        
        # Log creation if new instance
        if not self.pk or kwargs.get('force_insert'):
            try:
                created_by = getattr(self, '_created_by', None)
                AuditService.log_action(
                    action='create',
                    user=created_by,
                    obj=self
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error creating audit log: {e}")


class TimestampMixin(models.Model):
    """
    Mixin to add created_at and updated_at timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
