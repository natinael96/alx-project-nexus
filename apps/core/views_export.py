"""
Views for data export functionality.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.jobs.models import Job, Application
from apps.accounts.models import User
from apps.core.export_service import ExportService
from apps.accounts.permissions import IsEmployerOrAdmin
import logging

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='get',
    operation_summary='Export jobs',
    operation_description='Export jobs data to CSV or JSON format. Admin/Employer only.',
    manual_parameters=[
        openapi.Parameter(
            'format',
            openapi.IN_QUERY,
            description='Export format (csv or json)',
            type=openapi.TYPE_STRING,
            enum=['csv', 'json'],
            default='csv'
        ),
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Filter by job status',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'employer',
            openapi.IN_QUERY,
            description='Filter by employer ID (for employers, only their jobs)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: 'Export file',
        403: 'Forbidden',
    }
)
@api_view(['GET'])
@permission_classes([IsEmployerOrAdmin])
def export_jobs(request):
    """Export jobs data."""
    format_type = request.query_params.get('format', 'csv').lower()
    
    if format_type not in ['csv', 'json']:
        return Response(
            {'error': 'Invalid format. Use csv or json'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get queryset
    queryset = Job.objects.select_related('category', 'employer')
    
    # Filter by employer if not admin
    if not request.user.is_admin:
        queryset = queryset.filter(employer=request.user)
    elif request.query_params.get('employer'):
        queryset = queryset.filter(employer_id=request.query_params.get('employer'))
    
    # Filter by status
    if request.query_params.get('status'):
        queryset = queryset.filter(status=request.query_params.get('status'))
    
    # Export
    return ExportService.export_jobs(queryset, format_type)


@swagger_auto_schema(
    method='get',
    operation_summary='Export applications',
    operation_description='Export applications data to CSV or JSON format. Admin/Employer only.',
    manual_parameters=[
        openapi.Parameter(
            'format',
            openapi.IN_QUERY,
            description='Export format (csv or json)',
            type=openapi.TYPE_STRING,
            enum=['csv', 'json'],
            default='csv'
        ),
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Filter by application status',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'job',
            openapi.IN_QUERY,
            description='Filter by job ID',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: 'Export file',
        403: 'Forbidden',
    }
)
@api_view(['GET'])
@permission_classes([IsEmployerOrAdmin])
def export_applications(request):
    """Export applications data."""
    format_type = request.query_params.get('format', 'csv').lower()
    
    if format_type not in ['csv', 'json']:
        return Response(
            {'error': 'Invalid format. Use csv or json'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get queryset
    queryset = Application.objects.select_related('job', 'applicant', 'job__employer')
    
    # Filter by employer if not admin
    if not (request.user.is_authenticated and request.user.is_admin):
        queryset = queryset.filter(job__employer=request.user)
    
    # Filter by status
    if request.query_params.get('status'):
        queryset = queryset.filter(status=request.query_params.get('status'))
    
    # Filter by job
    if request.query_params.get('job'):
        queryset = queryset.filter(job_id=request.query_params.get('job'))
    
    # Export
    return ExportService.export_applications(queryset, format_type)


@swagger_auto_schema(
    method='get',
    operation_summary='Export users',
    operation_description='Export users data to CSV or JSON format. Admin only.',
    manual_parameters=[
        openapi.Parameter(
            'format',
            openapi.IN_QUERY,
            description='Export format (csv or json)',
            type=openapi.TYPE_STRING,
            enum=['csv', 'json'],
            default='csv'
        ),
        openapi.Parameter(
            'role',
            openapi.IN_QUERY,
            description='Filter by user role',
            type=openapi.TYPE_STRING,
            required=False
        ),
    ],
    responses={
        200: 'Export file',
        403: 'Forbidden - Admin access required',
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_users(request):
    """Export users data."""
    format_type = request.query_params.get('format', 'csv').lower()
    
    if format_type not in ['csv', 'json']:
        return Response(
            {'error': 'Invalid format. Use csv or json'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get queryset
    queryset = User.objects.all()
    
    # Filter by role
    if request.query_params.get('role'):
        queryset = queryset.filter(role=request.query_params.get('role'))
    
    # Export
    return ExportService.export_users(queryset, format_type)
