"""
Security service for managing API keys, IP whitelisting, and security events.
"""
import hashlib
import secrets
import logging
from typing import Optional
from datetime import datetime
from django.utils import timezone
from apps.core.models_security import APIKey, IPWhitelist, SecurityEvent
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class SecurityService:
    """
    Service for security-related operations.
    """
    
    @staticmethod
    def hash_api_key(key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def create_api_key(
        user: User,
        name: str,
        expires_at: Optional[datetime] = None,
        rate_limit: int = 1000,
        allowed_ips: Optional[str] = None,
        scopes: Optional[list] = None
    ) -> tuple:
        """
        Create a new API key.
        
        Returns:
            Tuple of (plain_key, api_key_instance)
        """
        # Generate plain key
        plain_key = APIKey.generate_key()
        
        # Hash the key for storage
        hashed_key = SecurityService.hash_api_key(plain_key)
        
        # Create API key instance
        api_key = APIKey.objects.create(
            name=name,
            key=hashed_key,
            user=user,
            expires_at=expires_at,
            rate_limit=rate_limit,
            allowed_ips=allowed_ips or '',
            scopes=scopes or []
        )
        
        logger.info(f"API key created for user {user.username}: {name}")
        return plain_key, api_key
    
    @staticmethod
    def validate_api_key(key: str, ip_address: Optional[str] = None) -> Optional[APIKey]:
        """
        Validate an API key.
        
        Returns:
            APIKey instance if valid, None otherwise
        """
        hashed_key = SecurityService.hash_api_key(key)
        
        try:
            api_key = APIKey.objects.get(key=hashed_key, is_active=True)
            
            # Check expiration
            if api_key.is_expired():
                SecurityService.log_security_event(
                    'api_key_abuse',
                    user=api_key.user,
                    ip_address=ip_address,
                    details={'reason': 'expired_key'}
                )
                return None
            
            # Check IP whitelist
            if ip_address and not api_key.check_ip_allowed(ip_address):
                SecurityService.log_security_event(
                    'api_key_abuse',
                    user=api_key.user,
                    ip_address=ip_address,
                    details={'reason': 'ip_not_allowed'}
                )
                return None
            
            # Update last used
            api_key.update_last_used()
            
            return api_key
        except APIKey.DoesNotExist:
            SecurityService.log_security_event(
                'api_key_abuse',
                ip_address=ip_address,
                details={'reason': 'invalid_key'}
            )
            return None
    
    @staticmethod
    def revoke_api_key(api_key: APIKey):
        """Revoke an API key."""
        api_key.is_active = False
        api_key.save(update_fields=['is_active', 'updated_at'])
        logger.info(f"API key revoked: {api_key.name}")
    
    @staticmethod
    def is_ip_whitelisted(ip_address: str) -> bool:
        """Check if an IP address is whitelisted."""
        return IPWhitelist.objects.filter(
            ip_address=ip_address,
            is_active=True
        ).exists()
    
    @staticmethod
    def add_ip_to_whitelist(ip_address: str, description: str = '', created_by: Optional[User] = None) -> IPWhitelist:
        """Add an IP address to the whitelist."""
        whitelist, created = IPWhitelist.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'description': description,
                'created_by': created_by,
                'is_active': True
            }
        )
        if not created:
            whitelist.is_active = True
            whitelist.description = description
            whitelist.save(update_fields=['is_active', 'description', 'updated_at'])
        
        logger.info(f"IP address whitelisted: {ip_address}")
        return whitelist
    
    @staticmethod
    def remove_ip_from_whitelist(ip_address: str):
        """Remove an IP address from the whitelist."""
        IPWhitelist.objects.filter(ip_address=ip_address).update(is_active=False)
        logger.info(f"IP address removed from whitelist: {ip_address}")
    
    @staticmethod
    def log_security_event(
        event_type: str,
        user: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None
    ):
        """Log a security event."""
        try:
            SecurityEvent.objects.create(
                event_type=event_type,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent or '',
                details=details or {}
            )
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
