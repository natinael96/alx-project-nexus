"""
Serializers for user profile enhancements.
"""
from rest_framework import serializers
from .models import User
from .models_profile import (
    Skill, Education, WorkHistory, Portfolio,
    SocialLink, UserPreferences, SavedJob
)
from apps.jobs.models import Job


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for Skill model.
    """
    class Meta:
        model = Skill
        fields = (
            'id', 'name', 'level', 'years_of_experience',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_name(self, value):
        """Validate skill name."""
        return value.strip().title()


class EducationSerializer(serializers.ModelSerializer):
    """
    Serializer for Education model.
    """
    class Meta:
        model = Education
        fields = (
            'id', 'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'is_current', 'description',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        """Validate education data."""
        if attrs.get('is_current') and attrs.get('end_date'):
            raise serializers.ValidationError({
                'end_date': 'Current education cannot have an end date.'
            })
        if attrs.get('end_date') and attrs.get('start_date'):
            if attrs['end_date'] < attrs['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        return attrs


class WorkHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for WorkHistory model.
    """
    class Meta:
        model = WorkHistory
        fields = (
            'id', 'company', 'position', 'start_date', 'end_date',
            'is_current', 'description', 'location',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        """Validate work history data."""
        if attrs.get('is_current') and attrs.get('end_date'):
            raise serializers.ValidationError({
                'end_date': 'Current job cannot have an end date.'
            })
        if attrs.get('end_date') and attrs.get('start_date'):
            if attrs['end_date'] < attrs['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        return attrs


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Serializer for Portfolio model.
    """
    class Meta:
        model = Portfolio
        fields = (
            'id', 'title', 'description', 'url', 'technologies',
            'start_date', 'end_date', 'is_featured',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_technologies(self, value):
        """Clean technologies string."""
        if value:
            # Remove extra spaces and normalize
            techs = [t.strip() for t in value.split(',') if t.strip()]
            return ', '.join(techs)
        return value


class SocialLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for SocialLink model.
    """
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    
    class Meta:
        model = SocialLink
        fields = (
            'id', 'platform', 'platform_display', 'url', 'is_public',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'platform_display', 'created_at', 'updated_at')
    
    def validate_url(self, value):
        """Validate URL format."""
        from django.core.validators import URLValidator
        from django.core.exceptions import ValidationError
        validator = URLValidator()
        try:
            validator(value)
        except ValidationError:
            raise serializers.ValidationError('Invalid URL format.')
        return value


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializer for UserPreferences model.
    """
    class Meta:
        model = UserPreferences
        fields = (
            'email_job_alerts', 'email_application_updates', 'email_new_jobs',
            'email_newsletter', 'alert_frequency', 'profile_visibility',
            'show_email', 'show_phone', 'show_location', 'resume_visibility',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class SavedJobSerializer(serializers.ModelSerializer):
    """
    Serializer for SavedJob model.
    """
    job = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedJob
        fields = ('id', 'job', 'notes', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def get_job(self, obj):
        """Return job details."""
        from apps.jobs.serializers import JobListSerializer
        return JobListSerializer(obj.job).data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Comprehensive user profile serializer with all enhancements.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    work_history = WorkHistorySerializer(many=True, read_only=True)
    portfolio = PortfolioSerializer(many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)
    preferences = UserPreferencesSerializer(read_only=True)
    profile_completion = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'phone_number', 'profile_picture',
            'bio', 'skills', 'education', 'work_history', 'portfolio',
            'social_links', 'preferences', 'profile_completion',
            'date_joined', 'last_login'
        )
        read_only_fields = (
            'id', 'username', 'email', 'role', 'date_joined', 'last_login',
            'full_name', 'profile_completion'
        )
    
    def get_profile_completion(self, obj):
        """Calculate profile completion percentage."""
        from apps.accounts.utils import calculate_profile_completion
        return calculate_profile_completion(obj)
