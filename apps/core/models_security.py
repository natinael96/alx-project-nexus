"""
Security-related models for API keys and IP whitelisting.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from apps.accounts.models import User
from apps.core.models_base import UUIDModel
import secrets


class APIKey(UUIDModel):
    """
    Model for managing API keys for programmatic access.
    """
    name = models.CharField(
        max_length=255,
        help_text='Descriptive name for the API key'
    )
    key = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text='The API key (hashed)'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text='User who owns this API key'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this API key is active'
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time this key was used'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Expiration date (null = never expires)'
    )
    rate_limit = models.PositiveIntegerField(
        default=1000,
        help_text='Rate limit per hour for this key'
    )
    allowed_ips = models.TextField(
        blank=True,
        help_text='Comma-separated list of allowed IP addresses (empty = all)'
    )
    scopes = models.JSONField(
        default=list,
        help_text='List of allowed scopes/permissions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['key', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    @staticmethod
    def generate_key():
        """Generate a new API key."""
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        """Check if the API key is expired."""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if the API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
    
    def update_last_used(self):
        """Update the last used timestamp."""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at', 'updated_at'])
    
    def check_ip_allowed(self, ip_address):
        """Check if an IP address is allowed."""
        if not self.allowed_ips:
            return True
        allowed_ips = [ip.strip() for ip in self.allowed_ips.split(',')]
        return ip_address in allowed_ips


class IPWhitelist(UUIDModel):
    """
    Model for IP whitelisting (e.g., for admin access).
    """
    ip_address = models.GenericIPAddressField(
        help_text='IP address to whitelist'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Description of why this IP is whitelisted'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this whitelist entry is active'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_ip_whitelists',
        help_text='User who created this whitelist entry'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ip_whitelist'
        verbose_name = 'IP Whitelist'
        verbose_name_plural = 'IP Whitelists'
        unique_together = [['ip_address']]
        indexes = [
            models.Index(fields=['ip_address', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.description or 'No description'}"


class SecurityEvent(UUIDModel):
    """
    Model for tracking security events (failed logins, suspicious activity, etc.).
    """
    EVENT_TYPES = [
        ('failed_login', 'Failed Login'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('api_key_abuse', 'API Key Abuse'),
        ('password_reset_attempt', 'Password Reset Attempt'),
        ('account_locked', 'Account Locked'),
        ('other', 'Other'),
    ]
    
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_events'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True
    )
    details = models.JSONField(
        default=dict,
        help_text='Additional event details'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'security_events'
        verbose_name = 'Security Event'
        verbose_name_plural = 'Security Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{self.event_type} - {user_str} - {self.created_at}"
