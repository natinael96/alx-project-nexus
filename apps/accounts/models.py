"""
User models for the Job Board Platform.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser with UUID primary key.
    Supports role-based access control (admin, employer, user).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for this user'
    )
    """
    Custom User model extending Django's AbstractUser.
    Supports role-based access control (admin, employer, user).
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employer', 'Employer'),
        ('user', 'User'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text='User role for access control'
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        help_text='User profile picture'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text='Short bio about the user'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']  # Newest users first by default
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_employer(self):
        """Check if user is an employer."""
        return self.role == 'employer'
    
    @property
    def is_regular_user(self):
        """Check if user is a regular user."""
        return self.role == 'user'
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip() or self.username

