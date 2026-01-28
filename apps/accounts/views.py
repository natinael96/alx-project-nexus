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
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer
)
from .permissions import IsAdminUser


@swagger_auto_schema(
    method='post',
    request_body=UserRegistrationSerializer,
    responses={
        201: UserSerializer,
        400: 'Bad Request'
    },
    operation_summary='Register a new user',
    operation_description='Create a new user account with role-based access (admin, employer, user)'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
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
    operation_description='Authenticate user and return JWT tokens'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return JWT tokens."""
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
    operation_description='Get a new access token using refresh token'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh access token."""
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = RefreshToken(refresh_token)
        return Response({
            'access': str(token.access_token)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Invalid refresh token'},
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
    operation_description='Update the currently authenticated user profile'
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_current_user(request):
    """Update current authenticated user."""
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
    operation_description='Change the password for the currently authenticated user'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password."""
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListAPIView(generics.ListAPIView):
    """List all users (Admin only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user (Admin only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

