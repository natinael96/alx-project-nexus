"""
Views for job enhancement features.
"""
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from .models import Job
from .models_job_enhancements import (
    JobView, JobShare, JobRecommendation, JobAnalytics, ApplicationSource
)
from .serializers_job_enhancements import (
    JobShareSerializer, JobRecommendationSerializer,
    JobAnalyticsSerializer, ApplicationSourceSerializer
)
from apps.accounts.permissions import IsEmployerOrAdmin, IsAdminUser
from apps.accounts.models import User
import logging

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='post',
    operation_summary='Share a job',
    operation_description='Share a job via email, link, or social media.',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'job_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
            'method': openapi.Schema(type=openapi.TYPE_STRING, enum=['email', 'link', 'social', 'other']),
            'shared_with': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['job_id', 'method']
    ),
    responses={
        201: JobShareSerializer,
        400: 'Bad Request',
        404: 'Job not found',
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def share_job(request):
    """Share a job."""
    job_id = request.data.get('job_id')
    method = request.data.get('method')
    shared_with = request.data.get('shared_with', '')
    
    if not job_id or not method:
        return Response(
            {'error': 'job_id and method are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        job = Job.objects.get(id=job_id, status='active')
    except Job.DoesNotExist:
        return Response(
            {'error': 'Job not found or not active'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    share = JobShare.objects.create(
        job=job,
        user=request.user if request.user.is_authenticated else None,
        method=method,
        shared_with=shared_with
    )
    
    # Update analytics
    try:
        analytics, _ = JobAnalytics.objects.get_or_create(job=job)
        analytics.shares_count = JobShare.objects.filter(job=job).count()
        analytics.save()
    except Exception as e:
        logger.error(f"Error updating job analytics: {e}")
    
    serializer = JobShareSerializer(share)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='get',
    operation_summary='Get similar jobs',
    operation_description='Get jobs similar to a given job based on category, location, and job type.',
    manual_parameters=[
        openapi.Parameter(
            'job_id',
            openapi.IN_QUERY,
            description='Job ID (UUID) to find similar jobs for',
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            required=True
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description='Maximum number of similar jobs (default: 5)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: 'List of similar jobs',
        404: 'Job not found',
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def similar_jobs(request):
    """Get similar jobs."""
    job_id = request.query_params.get('job_id')
    limit = int(request.query_params.get('limit', 5))
    
    if not job_id:
        return Response(
            {'error': 'job_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        job = Job.objects.get(id=job_id, status='active')
    except Job.DoesNotExist:
        return Response(
            {'error': 'Job not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Find similar jobs
    similar = Job.objects.filter(
        status='active'
    ).exclude(
        id=job.id
    ).filter(
        Q(category=job.category) |
        Q(location__icontains=job.location.split(',')[0]) |
        Q(job_type=job.job_type)
    ).annotate(
        similarity_score=Count('id')  # Simple scoring
    ).order_by('-is_featured', '-similarity_score', '-created_at')[:limit]
    
    from .serializers import JobListSerializer
    serializer = JobListSerializer(similar, many=True)
    return Response({
        'job_id': job_id,
        'similar_jobs': serializer.data,
        'count': len(serializer.data)
    })


@swagger_auto_schema(
    method='get',
    operation_summary='Get job analytics',
    operation_description='Get analytics for a specific job. Employer/Admin only.',
    responses={
        200: JobAnalyticsSerializer,
        403: 'Forbidden',
        404: 'Job not found',
    }
)
@api_view(['GET'])
@permission_classes([IsEmployerOrAdmin])
def job_analytics(request, job_id):
    """Get job analytics."""
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response(
            {'error': 'Job not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if not request.user.is_admin and job.employer != request.user:
        return Response(
            {'error': 'You do not have permission to view analytics for this job'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    analytics, created = JobAnalytics.objects.get_or_create(job=job)
    if not created:
        analytics.update_metrics()
    
    serializer = JobAnalyticsSerializer(analytics)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_summary='Get employer dashboard',
    operation_description='Get comprehensive dashboard statistics for an employer.',
    responses={
        200: 'Dashboard statistics',
        403: 'Forbidden - Employer access required',
    }
)
@api_view(['GET'])
@permission_classes([IsEmployerOrAdmin])
def employer_dashboard(request):
    """Get employer dashboard statistics."""
    user = request.user
    
    # Get employer's jobs
    if user.is_admin:
        jobs = Job.objects.all()
    else:
        jobs = Job.objects.filter(employer=user)
    
    # Job statistics
    total_jobs = jobs.count()
    active_jobs = jobs.filter(status='active').count()
    draft_jobs = jobs.filter(status='draft').count()
    closed_jobs = jobs.filter(status='closed').count()
    pending_approval = jobs.filter(approval_status='pending').count()
    
    # Application statistics
    from .models import Application
    applications = Application.objects.filter(job__employer=user)
    total_applications = applications.count()
    pending_applications = applications.filter(status='pending').count()
    accepted_applications = applications.filter(status='accepted').count()
    rejected_applications = applications.filter(status='rejected').count()
    
    # View statistics
    total_views = JobView.objects.filter(job__employer=user).count()
    unique_views = JobView.objects.filter(job__employer=user).values('user', 'ip_address').distinct().count()
    
    # Recent jobs (last 5)
    recent_jobs = jobs.order_by('-created_at')[:5]
    from .serializers import JobListSerializer
    recent_jobs_data = JobListSerializer(recent_jobs, many=True).data
    
    # Recent applications (last 5)
    recent_applications = applications.select_related('applicant', 'job').order_by('-applied_at')[:5]
    from .serializers import ApplicationSerializer
    recent_applications_data = ApplicationSerializer(recent_applications, many=True).data
    
    # Top performing jobs (by views)
    top_jobs = jobs.annotate(
        view_count=Count('views')
    ).order_by('-view_count', '-created_at')[:5]
    top_jobs_data = JobListSerializer(top_jobs, many=True).data
    
    return Response({
        'statistics': {
            'jobs': {
                'total': total_jobs,
                'active': active_jobs,
                'draft': draft_jobs,
                'closed': closed_jobs,
                'pending_approval': pending_approval,
            },
            'applications': {
                'total': total_applications,
                'pending': pending_applications,
                'accepted': accepted_applications,
                'rejected': rejected_applications,
            },
            'views': {
                'total': total_views,
                'unique': unique_views,
            },
        },
        'recent_jobs': recent_jobs_data,
        'recent_applications': recent_applications_data,
        'top_jobs': top_jobs_data,
    })


@swagger_auto_schema(
    method='get',
    operation_summary='Get job recommendations',
    operation_description='Get personalized job recommendations for the authenticated user.',
    manual_parameters=[
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description='Maximum number of recommendations (default: 10)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: JobRecommendationSerializer(many=True),
        401: 'Unauthorized',
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_recommendations(request):
    """Get job recommendations for user."""
    limit = int(request.query_params.get('limit', 10))
    
    # Get user's recommendations
    recommendations = JobRecommendation.objects.filter(
        user=request.user,
        job__status='active'
    ).select_related('job').order_by('-score', '-created_at')[:limit]
    
    serializer = JobRecommendationSerializer(recommendations, many=True)
    return Response({
        'recommendations': serializer.data,
        'count': len(serializer.data)
    })


class JobShareViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job shares.
    """
    serializer_class = JobShareSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Return shares for the current user or all shares if admin."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return JobShare.objects.none()
        
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return JobShare.objects.all()
        
        if not self.request.user.is_authenticated:
            return JobShare.objects.none()
        
        return JobShare.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating a share."""
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)
