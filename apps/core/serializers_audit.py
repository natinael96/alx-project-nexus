"""
Serializers for audit logging models.
"""
from rest_framework import serializers
from apps.core.models_audit import AuditLog, ChangeHistory
from apps.accounts.models import User


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for AuditLog model.
    """
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    content_type_name = serializers.CharField(source='content_type.model', read_only=True, allow_null=True)
    
    class Meta:
        model = AuditLog
        fields = (
            'id', 'user', 'user_name', 'action', 'action_display',
            'content_type', 'content_type_name', 'object_id',
            'object_repr', 'changes', 'ip_address', 'user_agent',
            'request_path', 'request_method', 'metadata', 'created_at'
        )
        read_only_fields = '__all__'


class ChangeHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for ChangeHistory model.
    """
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True, allow_null=True)
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = ChangeHistory
        fields = (
            'id', 'content_type', 'content_type_name', 'object_id',
            'changed_by', 'changed_by_name', 'field_name',
            'old_value', 'new_value', 'change_reason', 'created_at'
        )
        read_only_fields = '__all__'
