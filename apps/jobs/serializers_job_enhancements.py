"""
Serializers for job enhancement models.
"""
from rest_framework import serializers
from .models import Job
from .models_job_enhancements import (
    JobView, JobShare, JobRecommendation, JobAnalytics, ApplicationSource
)
from apps.accounts.models import User


class JobShareSerializer(serializers.ModelSerializer):
    """
    Serializer for JobShare model.
    """
    job_title = serializers.CharField(source='job.title', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    
    class Meta:
        model = JobShare
        fields = (
            'id', 'job', 'job_title', 'method', 'method_display',
            'shared_with', 'shared_at'
        )
        read_only_fields = ('id', 'shared_at')
    
    def validate(self, attrs):
        """Validate share data."""
        job = attrs.get('job')
        if job and job.status != 'active':
            raise serializers.ValidationError({
                'job': 'Can only share active jobs.'
            })
        return attrs


class JobRecommendationSerializer(serializers.ModelSerializer):
    """
    Serializer for JobRecommendation model.
    """
    job = serializers.SerializerMethodField()
    
    class Meta:
        model = JobRecommendation
        fields = (
            'id', 'job', 'score', 'reason', 'viewed', 'clicked', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
    
    def get_job(self, obj):
        """Return job details."""
        from .serializers import JobListSerializer
        return JobListSerializer(obj.job).data


class JobAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for JobAnalytics model.
    """
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = JobAnalytics
        fields = (
            'id', 'job', 'job_title', 'total_views', 'unique_views',
            'total_applications', 'shares_count', 'saved_count', 'last_updated'
        )
        read_only_fields = '__all__'


class ApplicationSourceSerializer(serializers.ModelSerializer):
    """
    Serializer for ApplicationSource model.
    """
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    
    class Meta:
        model = ApplicationSource
        fields = (
            'id', 'application', 'source_type', 'source_type_display',
            'referrer_url', 'campaign', 'utm_source', 'utm_medium',
            'utm_campaign', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
