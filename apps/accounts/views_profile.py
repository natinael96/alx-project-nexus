"""
Views for user profile enhancements and dashboard.
"""
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import User
from .models_profile import (
    Skill, Education, WorkHistory, Portfolio,
    SocialLink, UserPreferences, SavedJob
)
from .serializers_profile import (
    SkillSerializer, EducationSerializer, WorkHistorySerializer,
    PortfolioSerializer, SocialLinkSerializer, UserPreferencesSerializer,
    SavedJobSerializer, UserProfileSerializer
)
from apps.jobs.models import Application, Job
from apps.jobs.serializers import JobListSerializer, ApplicationSerializer
import logging

logger = logging.getLogger(__name__)


class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user skills.
    """
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's skills."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return Skill.objects.none()
        
        if not self.request.user.is_authenticated:
            return Skill.objects.none()
        
        return Skill.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating a skill."""
        serializer.save(user=self.request.user)


class EducationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user education.
    """
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's education."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return Education.objects.none()
        
        if not self.request.user.is_authenticated:
            return Education.objects.none()
        
        return Education.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating education."""
        serializer.save(user=self.request.user)


class WorkHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user work history.
    """
    serializer_class = WorkHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's work history."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return WorkHistory.objects.none()
        
        if not self.request.user.is_authenticated:
            return WorkHistory.objects.none()
        
        return WorkHistory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating work history."""
        serializer.save(user=self.request.user)


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user portfolio.
    """
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's portfolio."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return Portfolio.objects.none()
        
        if not self.request.user.is_authenticated:
            return Portfolio.objects.none()
        
        return Portfolio.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating portfolio item."""
        serializer.save(user=self.request.user)


class SocialLinkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user social links.
    """
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's social links."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return SocialLink.objects.none()
        
        if not self.request.user.is_authenticated:
            return SocialLink.objects.none()
        
        return SocialLink.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating social link."""
        serializer.save(user=self.request.user)


class UserPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user preferences.
    """
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's preferences."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return UserPreferences.objects.none()
        
        if not self.request.user.is_authenticated:
            return UserPreferences.objects.none()
        
        return UserPreferences.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create preferences for the user."""
        preferences, created = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences
    
    def perform_create(self, serializer):
        """Set the user when creating preferences."""
        serializer.save(user=self.request.user)


class SavedJobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved jobs/bookmarks.
    """
    serializer_class = SavedJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's saved jobs."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return SavedJob.objects.none()
        
        if not self.request.user.is_authenticated:
            return SavedJob.objects.none()
        
        return SavedJob.objects.filter(user=self.request.user).select_related('job')
    
    def perform_create(self, serializer):
        """Set the user when creating saved job."""
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        method='post',
        operation_summary='Save a job',
        operation_description='Save/bookmark a job for later.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'job_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                'notes': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['job_id']
        ),
        responses={
            201: 'Job saved successfully',
            400: 'Bad Request - Job already saved or invalid job ID',
        }
    )
    @action(detail=False, methods=['post'])
    def save_job(self, request):
        """Save a job."""
        job_id = request.data.get('job_id')
        notes = request.data.get('notes', '')
        
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job = Job.objects.get(id=job_id, status='active')
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found or not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already saved
        saved_job, created = SavedJob.objects.get_or_create(
            user=request.user,
            job=job,
            defaults={'notes': notes}
        )
        
        if not created:
            # Update notes if already saved
            saved_job.notes = notes
            saved_job.save(update_fields=['notes'])
        
        serializer = SavedJobSerializer(saved_job)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @swagger_auto_schema(
        method='delete',
        operation_summary='Unsave a job',
        operation_description='Remove a job from saved jobs.',
        responses={
            204: 'Job unsaved successfully',
            404: 'Saved job not found',
        }
    )
    @action(detail=True, methods=['delete'])
    def unsave(self, request, pk=None):
        """Unsave a job."""
        saved_job = self.get_object()
        saved_job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='get',
    operation_summary='Get user profile',
    operation_description='Get comprehensive user profile with all enhancements.',
    responses={
        200: UserProfileSerializer,
        401: 'Unauthorized',
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get comprehensive user profile."""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_summary='Get user dashboard',
    operation_description='Get user dashboard with statistics, saved jobs, and application history.',
    responses={
        200: 'Dashboard data',
        401: 'Unauthorized',
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """Get user dashboard data."""
    user = request.user
    
    # Application statistics
    total_applications = Application.objects.filter(applicant=user).count()
    pending_applications = Application.objects.filter(
        applicant=user,
        status='pending'
    ).count()
    accepted_applications = Application.objects.filter(
        applicant=user,
        status='accepted'
    ).count()
    rejected_applications = Application.objects.filter(
        applicant=user,
        status='rejected'
    ).count()
    
    # Recent applications (last 5)
    recent_applications = Application.objects.filter(
        applicant=user
    ).select_related('job', 'job__employer', 'job__category').order_by('-applied_at')[:5]
    
    # Saved jobs count
    saved_jobs_count = SavedJob.objects.filter(user=user).count()
    
    # Recent saved jobs (last 5)
    recent_saved_jobs = SavedJob.objects.filter(
        user=user
    ).select_related('job', 'job__employer', 'job__category').order_by('-created_at')[:5]
    
    # Profile completion
    from apps.accounts.utils import calculate_profile_completion
    profile_completion = calculate_profile_completion(user)
    
    # Application history (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    applications_last_30_days = Application.objects.filter(
        applicant=user,
        applied_at__gte=thirty_days_ago
    ).count()
    
    return Response({
        'statistics': {
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'accepted_applications': accepted_applications,
            'rejected_applications': rejected_applications,
            'saved_jobs_count': saved_jobs_count,
            'applications_last_30_days': applications_last_30_days,
        },
        'recent_applications': ApplicationSerializer(recent_applications, many=True).data,
        'recent_saved_jobs': SavedJobSerializer(recent_saved_jobs, many=True).data,
        'profile_completion': profile_completion,
    })
