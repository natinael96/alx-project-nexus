"""
OAuth2 and social authentication views.
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()
logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='get',
    operation_summary='OAuth2 login URL',
    operation_description='Get OAuth2 login URL for Google or LinkedIn.',
    manual_parameters=[
        openapi.Parameter(
            'provider',
            openapi.IN_QUERY,
            description='OAuth provider (google or linkedin)',
            type=openapi.TYPE_STRING,
            enum=['google', 'linkedin'],
            required=True
        ),
    ],
    responses={
        200: openapi.Response('OAuth URL'),
        400: 'Invalid provider',
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_login_url(request):
    """
    Get OAuth2 login URL for social authentication.
    This is a placeholder - in production, use django-allauth or similar.
    """
    provider = request.query_params.get('provider')
    
    if provider not in ['google', 'linkedin']:
        return Response(
            {'error': 'Invalid provider. Use "google" or "linkedin".'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Placeholder implementation
    # In production, integrate with django-allauth or OAuth2 library
    oauth_url = f"/accounts/{provider}/login/"
    
    return Response({
        'oauth_url': oauth_url,
        'provider': provider,
        'message': 'Redirect user to this URL for OAuth authentication'
    })


@swagger_auto_schema(
    method='post',
    operation_summary='OAuth2 callback',
    operation_description='Handle OAuth2 callback and create/login user.',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'code': openapi.Schema(type=openapi.TYPE_STRING, description='OAuth authorization code'),
            'provider': openapi.Schema(type=openapi.TYPE_STRING, description='OAuth provider'),
        },
        required=['code', 'provider']
    ),
    responses={
        200: openapi.Response('User authenticated', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
                'user': openapi.Schema(type=openapi.TYPE_OBJECT),
            }
        )),
        400: 'Invalid code or provider',
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def oauth_callback(request):
    """
    Handle OAuth2 callback.
    This is a placeholder - in production, use django-allauth or similar.
    """
    code = request.data.get('code')
    provider = request.data.get('provider')
    
    if not code or not provider:
        return Response(
            {'error': 'code and provider are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Placeholder implementation
    # In production:
    # 1. Exchange code for access token
    # 2. Get user info from provider
    # 3. Create or get user
    # 4. Generate JWT tokens
    # 5. Return tokens and user data
    
    return Response({
        'message': 'OAuth callback handler - implement with django-allauth or OAuth2 library',
        'provider': provider
    }, status=status.HTTP_501_NOT_IMPLEMENTED)
