"""
Views for security features (password reset, OAuth, API keys).
"""
import logging
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.accounts.serializers_security import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    APIKeySerializer,
    APIKeyCreateSerializer,
    IPWhitelistSerializer
)
from apps.core.security_service import SecurityService
from apps.core.models_security import APIKey, IPWhitelist
from apps.core.email_service import EmailService

User = get_user_model()
logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='post',
    operation_summary='Request password reset',
    operation_description='Request a password reset email.',
    request_body=PasswordResetRequestSerializer,
    responses={
        200: 'Password reset email sent (always returns success for security)',
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    Request a password reset email.
    Always returns success to prevent user enumeration.
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    
    try:
        user = User.objects.get(email=email, is_active=True)
        
        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Send reset email
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        EmailService.send_email(
            subject='Password Reset Request',
            template_name='emails/password_reset.html',
            context={
                'user': user,
                'reset_url': reset_url,
                'token': token,
                'uid': uid
            },
            recipient_list=[user.email]
        )
        
        # Log security event
        SecurityService.log_security_event(
            'password_reset_attempt',
            user=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'email': email}
        )
        
        logger.info(f"Password reset requested for user: {user.email}")
    except User.DoesNotExist:
        # Don't reveal if user exists
        pass
    
    # Always return success to prevent user enumeration
    return Response({
        'message': 'If an account with that email exists, a password reset link has been sent.'
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_summary='Confirm password reset',
    operation_description='Reset password using token from email.',
    request_body=PasswordResetConfirmSerializer,
    responses={
        200: 'Password reset successful',
        400: 'Invalid token or password validation failed',
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset with token."""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']
    
    # Extract uid from token (if provided separately) or from request
    uid = request.data.get('uid')
    
    if not uid:
        return Response(
            {'error': 'UID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Decode user ID
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id, is_active=True)
        
        # Verify token
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Log security event
        SecurityService.log_security_event(
            'password_reset_attempt',
            user=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'action': 'password_reset_successful'}
        )
        
        logger.info(f"Password reset successful for user: {user.email}")
        
        return Response({
            'message': 'Password has been reset successfully.'
        }, status=status.HTTP_200_OK)
        
    except (User.DoesNotExist, ValueError, TypeError):
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing API keys.
    """
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return API keys for the current user."""
        if self.request.user.is_admin:
            return APIKey.objects.select_related('user')
        return APIKey.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(
        operation_summary='Create API key',
        operation_description='Create a new API key. The plain key is only shown once.',
        request_body=APIKeyCreateSerializer,
        responses={
            201: openapi.Response('API key created', APIKeySerializer),
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new API key."""
        serializer = APIKeyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plain_key, api_key = SecurityService.create_api_key(
            user=request.user,
            name=serializer.validated_data['name'],
            expires_at=serializer.validated_data.get('expires_at'),
            rate_limit=serializer.validated_data.get('rate_limit', 1000),
            allowed_ips=serializer.validated_data.get('allowed_ips'),
            scopes=serializer.validated_data.get('scopes', [])
        )
        
        response_serializer = APIKeySerializer(api_key)
        response_data = response_serializer.data
        response_data['key'] = plain_key  # Only time the plain key is shown
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_summary='Revoke API key',
        operation_description='Revoke (deactivate) an API key.',
        responses={
            200: 'API key revoked',
        }
    )
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke an API key."""
        api_key = self.get_object()
        
        # Check permission
        if not request.user.is_admin and api_key.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        SecurityService.revoke_api_key(api_key)
        return Response({'message': 'API key revoked'}, status=status.HTTP_200_OK)


class IPWhitelistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing IP whitelist (Admin only).
    """
    serializer_class = IPWhitelistSerializer
    permission_classes = [IsAdminUser]
    queryset = IPWhitelist.objects.all()
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
