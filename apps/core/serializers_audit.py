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
    user_name = serializers.SerializerMethodField()
    action_display = serializers.SerializerMethodField()
    content_type_name = serializers.SerializerMethodField()
    
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    
    def get_action_display(self, obj):
        return obj.get_action_display()
    
    def get_content_type_name(self, obj):
        return obj.content_type.model if obj.content_type else None
    
    class Meta:
        model = AuditLog
        fields = (
            'id', 'user', 'user_name', 'action', 'action_display',
            'content_type', 'content_type_name', 'object_id',
            'object_repr', 'changes', 'ip_address', 'user_agent',
            'request_path', 'request_method', 'metadata', 'created_at'
        )
        read_only_fields = (
            'id', 'user', 'user_name', 'action', 'action_display',
            'content_type', 'content_type_name', 'object_id',
            'object_repr', 'changes', 'ip_address', 'user_agent',
            'request_path', 'request_method', 'metadata', 'created_at'
        )


class ChangeHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for ChangeHistory model.
    """
    changed_by_name = serializers.SerializerMethodField()
    content_type_name = serializers.SerializerMethodField()
    
    def get_changed_by_name(self, obj):
        return obj.changed_by.username if obj.changed_by else None
    
    def get_content_type_name(self, obj):
        return obj.content_type.model if obj.content_type else None
    
    class Meta:
        model = ChangeHistory
        fields = (
            'id', 'content_type', 'content_type_name', 'object_id',
            'changed_by', 'changed_by_name', 'field_name',
            'old_value', 'new_value', 'change_reason', 'created_at'
        )
        read_only_fields = (
            'id', 'content_type', 'content_type_name', 'object_id',
            'changed_by', 'changed_by_name', 'field_name',
            'old_value', 'new_value', 'change_reason', 'created_at'
        )
