"""
Views for accounts app - Authentication and User Management.
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import models as db_models
from apps.core.email_service import EmailService
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer
)
from .permissions import IsAdminUser
from apps.core.rate_limit import (
    rate_limit, RATE_LIMITS,
    rate_limit_login, rate_limit_register
)


@swagger_auto_schema(
    method='post',
    request_body=UserRegistrationSerializer,
    responses={
        201: UserSerializer,
        400: 'Bad Request'
    },
    operation_summary='Register a new user',
    operation_description='Create a new user account with role-based access (admin, employer, user). Passwords are validated for strength.'
)
@rate_limit(
    limit=RATE_LIMITS['register']['limit'],
    period=RATE_LIMITS['register']['period'],
    key_func=rate_limit_register,
    scope='register'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user.
    
    Security Features:
    - Password strength validation
    - Email uniqueness check
    - Username format validation
    - Prevents admin role registration
    - Passwords are hashed using Django's PBKDF2
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Send welcome email
        try:
            EmailService.send_welcome_email(user)
        except Exception as e:
            # Log error but don't fail registration
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send welcome email: {str(e)}")
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            description='Login successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: 'Bad Request',
        401: 'Unauthorized'
    },
    operation_summary='User login',
    operation_description='Authenticate user and return JWT tokens. Uses generic error messages to prevent user enumeration.'
)
@rate_limit(
    limit=RATE_LIMITS['login']['limit'],
    period=RATE_LIMITS['login']['period'],
    key_func=rate_limit_login,
    scope='login'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user and return JWT tokens.
    
    Security Features:
    - Generic error messages to prevent user enumeration
    - Checks if user account is active
    - Returns JWT access and refresh tokens
    - Updates last login timestamp
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['refresh']
    ),
    responses={
        200: openapi.Response(
            description='Token refreshed',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: 'Bad Request'
    },
    operation_summary='Refresh access token',
    operation_description='Get a new access token using refresh token. Invalid tokens return generic error messages.'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh access token.
    
    Security: Validates refresh token and returns new access token.
    Invalid or expired tokens return generic error message.
    """
    refresh_token_value = request.data.get('refresh')
    if not refresh_token_value:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = RefreshToken(refresh_token_value)
        # Verify token type and expiration
        token.verify()
        return Response({
            'access': str(token.access_token)
        }, status=status.HTTP_200_OK)
    except Exception:
        # Generic error message to prevent token enumeration
        return Response(
            {'error': 'Invalid or expired refresh token. Please login again.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@swagger_auto_schema(
    method='get',
    responses={
        200: UserSerializer,
        401: 'Unauthorized'
    },
    operation_summary='Get current user',
    operation_description='Get the currently authenticated user profile'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='put',
    request_body=UserSerializer,
    responses={
        200: UserSerializer,
        400: 'Bad Request',
        401: 'Unauthorized'
    },
    operation_summary='Update current user',
    operation_description='Update the currently authenticated user profile. Role changes are restricted to admins only.'
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_current_user(request):
    """
    Update current authenticated user.
    
    Security: Users cannot change their role unless they are admin.
    Email uniqueness is validated.
    """
    serializer = UserSerializer(
        request.user,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=ChangePasswordSerializer,
    responses={
        200: 'Password changed successfully',
        400: 'Bad Request',
        401: 'Unauthorized'
    },
    operation_summary='Change password',
    operation_description='Change the password for the currently authenticated user. All existing tokens should be invalidated after password change.'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password.
    
    Security Features:
    - Validates old password
    - Uses Django password validators for new password
    - Password confirmation check
    - Note: In production, consider invalidating all existing tokens
    
    Security Note: After password change, all existing JWT tokens should be invalidated.
    User must login again to get new tokens.
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        
        # Note: In a production system, you might want to blacklist all tokens here
        # This requires django-rest-framework-simplejwt[blacklist] to be installed
        # Example:
        # from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        # OutstandingToken.objects.filter(user=user).delete()
        
        return Response(
            {
                'message': 'Password changed successfully. Please login again with your new password.'
            },
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'role',
            openapi.IN_QUERY,
            description='Filter users by role (admin, employer, user)',
            type=openapi.TYPE_STRING,
            enum=['admin', 'employer', 'user']
        ),
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description='Search users by username, email, or full name',
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'is_active',
            openapi.IN_QUERY,
            description='Filter by active status (true/false)',
            type=openapi.TYPE_BOOLEAN
        ),
    ],
    responses={
        200: UserSerializer(many=True),
        401: 'Unauthorized',
        403: 'Forbidden - Admin access required'
    },
    operation_summary='List all users',
    operation_description='Get a paginated list of all users. Admin only. Supports filtering by role, search, and active status.'
)
class UserListAPIView(generics.ListAPIView):
    """
    List all users (Admin only).
    
    Features:
    - Filter by role
    - Search by username, email, or name
    - Filter by active status
    - Paginated results
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by role
        role = self.request.query_params.get('role', None)
        if role:
            if role in ['admin', 'employer', 'user']:
                queryset = queryset.filter(role=role)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        return queryset.select_related().order_by('-date_joined')


@swagger_auto_schema(
    method='get',
    responses={
        200: UserSerializer,
        401: 'Unauthorized',
        403: 'Forbidden - Admin access required',
        404: 'User not found'
    },
    operation_summary='Get user details',
    operation_description='Retrieve detailed information about a specific user. Admin only.'
)
@swagger_auto_schema(
    method='put',
    request_body=UserSerializer,
    responses={
        200: UserSerializer,
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden - Admin access required',
        404: 'User not found'
    },
    operation_summary='Update user',
    operation_description='Update user information. Admin only. Can change roles, activate/deactivate users.'
)
@swagger_auto_schema(
    method='delete',
    responses={
        204: 'User deleted successfully',
        401: 'Unauthorized',
        403: 'Forbidden - Admin access required',
        404: 'User not found',
        400: 'Cannot delete user (e.g., last admin or self-deletion)'
    },
    operation_summary='Delete user',
    operation_description='Delete a user account. Admin only. Prevents deletion of last admin and self-deletion.'
)
class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a user (Admin only).
    
    Security Features:
    - Prevents self-deletion
    - Prevents deleting the last admin
    - Validates role changes
    - Email uniqueness validation
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related()
    
    def update(self, request, *args, **kwargs):
        """Update user with additional security checks."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Additional validation for admin operations
        validated_data = serializer.validated_data
        
        # Prevent admins from demoting themselves
        if 'role' in validated_data:
            if instance == request.user and validated_data['role'] != 'admin':
                return Response(
                    {'role': 'You cannot change your own role from admin.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Prevent deactivating yourself
        if 'is_active' in validated_data:
            if instance == request.user and validated_data['is_active'] is False:
                return Response(
                    {'is_active': 'You cannot deactivate your own account.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete user with security checks."""
        instance = self.get_object()
        
        # Prevent self-deletion
        if instance == request.user:
            return Response(
                {'error': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent deleting the last admin
        if instance.is_admin:
            admin_count = User.objects.filter(role='admin', is_active=True).count()
            if admin_count <= 1:
                return Response(
                    {'error': 'Cannot delete the last active admin user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        self.perform_destroy(instance)
        return Response(
            {'message': 'User deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )