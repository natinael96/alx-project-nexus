"""
Serializers for accounts app.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        min_length=8,
        help_text='Password must be at least 8 characters long'
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'role', 'phone_number', 'bio'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'username': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email uniqueness and format."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower().strip()
    
    def validate_username(self, value):
        """Validate username format."""
        if len(value) < 3:
            raise serializers.ValidationError('Username must be at least 3 characters long.')
        if not value.replace('_', '').replace('.', '').isalnum():
            raise serializers.ValidationError('Username can only contain letters, numbers, underscores, and dots.')
        return value.lower().strip()
    
    def validate_role(self, value):
        """Prevent users from registering as admin."""
        if value == 'admin':
            raise serializers.ValidationError('Cannot register as admin. Please contact support.')
        return value
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create and return a new user with hashed password."""
        validated_data.pop('password2')
        password = validated_data.pop('password')
        # Ensure role defaults to 'user' if not provided
        if 'role' not in validated_data or not validated_data['role']:
            validated_data['role'] = 'user'
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'phone_number', 'profile_picture',
            'bio', 'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'date_joined', 'last_login')
    
    def validate_email(self, value):
        """Validate email uniqueness on update."""
        user = self.instance
        if user and User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower().strip() if value else value
    
    def validate_role(self, value):
        """Prevent non-admin users from changing their role."""
        user = self.instance
        if user and not user.is_admin and value != user.role:
            raise serializers.ValidationError('You cannot change your role. Please contact an administrator.')
        return value


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login. Supports both username and email."""
    username = serializers.CharField(
        required=True,
        help_text='Username or email address'
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Validate user credentials with security best practices.
        Supports login with either username or email address.
        """
        username_or_email = attrs.get('username', '').strip()
        password = attrs.get('password')
        
        if not username_or_email or not password:
            raise serializers.ValidationError({
                'non_field_errors': ['Username/email and password are required.']
            })
        
        # Determine if input is email or username
        user = None
        if '@' in username_or_email:
            # Input looks like an email - try to find user by email
            try:
                user = User.objects.get(email__iexact=username_or_email)
                # Authenticate using the username (not email)
                user = authenticate(username=user.username, password=password)
            except User.DoesNotExist:
                # User not found - will raise generic error below
                pass
        else:
            # Input is username - authenticate normally
            user = authenticate(username=username_or_email, password=password)
        
        if not user:
            # Generic error message to prevent user enumeration attacks
            # Don't reveal whether username/email exists or password is wrong
            raise serializers.ValidationError({
                'non_field_errors': ['Invalid credentials. Please check your username/email and password.']
            })
        
        if not user.is_active:
            raise serializers.ValidationError({
                'non_field_errors': ['This account has been disabled. Please contact support.']
            })
        
        attrs['user'] = user
        return attrs
    
    def create(self, validated_data):
        """Generate JWT tokens for authenticated user."""
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='Confirm New Password'
    )
    
    def validate(self, attrs):
        """Validate password change."""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

