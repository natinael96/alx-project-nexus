"""
Serializers for security features (password reset, OAuth, API keys).
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from apps.core.models_security import APIKey, IPWhitelist

User = get_user_model()


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate that the email exists."""
        if not User.objects.filter(email=value, is_active=True).exists():
            # Don't reveal if email exists for security
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })
        validate_password(attrs['new_password'])
        return attrs


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API key (without exposing the actual key)."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = APIKey
        fields = (
            'id', 'name', 'user', 'user_name', 'is_active',
            'last_used_at', 'expires_at', 'rate_limit',
            'allowed_ips', 'scopes', 'created_at', 'updated_at',
            'is_expired', 'is_valid'
        )
        read_only_fields = ('id', 'user', 'last_used_at', 'created_at', 'updated_at')


class APIKeyCreateSerializer(serializers.Serializer):
    """Serializer for creating API keys."""
    name = serializers.CharField(max_length=255, required=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    rate_limit = serializers.IntegerField(min_value=1, default=1000)
    allowed_ips = serializers.CharField(required=False, allow_blank=True)
    scopes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


class IPWhitelistSerializer(serializers.ModelSerializer):
    """Serializer for IP whitelist."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = IPWhitelist
        fields = (
            'id', 'ip_address', 'description', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
