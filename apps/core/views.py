"""
Core views for health checks and analytics.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .health import health_check, liveness_check, readiness_check
from .analytics import AnalyticsService
from apps.accounts.models import User


@swagger_auto_schema(
    method='get',
    operation_summary='Health check',
    operation_description='Comprehensive health check including database, cache, disk, and memory. Returns 200 if healthy, 503 if unhealthy.',
    responses={
        200: openapi.Response('All checks passed'),
        503: openapi.Response('One or more checks failed'),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_view(request):
    """Comprehensive health check endpoint."""
    return health_check(request)


@swagger_auto_schema(
    method='get',
    operation_summary='Liveness check',
    operation_description='Simple liveness check. Returns 200 if application is running.',
    responses={200: openapi.Response('Application is alive')}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check_view(request):
    """Simple liveness check endpoint."""
    return liveness_check(request)


@swagger_auto_schema(
    method='get',
    operation_summary='Readiness check',
    operation_description='Readiness check. Returns 200 if application is ready to serve traffic, 503 if not ready.',
    responses={
        200: openapi.Response('Application is ready'),
        503: openapi.Response('Application is not ready'),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check_view(request):
    """Readiness check endpoint."""
    return readiness_check(request)


@swagger_auto_schema(
    method='get',
    operation_summary='Get platform statistics',
    operation_description='Get comprehensive platform statistics including users, jobs, applications, and categories. Admin only.',
    responses={
        200: openapi.Response('Statistics retrieved successfully'),
        403: 'Forbidden - Admin access required',
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def statistics_view(request):
    """Get comprehensive platform statistics."""
    stats = AnalyticsService.get_overall_statistics()
    return Response(stats, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_summary='Get user statistics',
    operation_description='Get user-related statistics. Admin only.',
    responses={
        200: openapi.Response('User statistics retrieved'),
        403: 'Forbidden - Admin access required',
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_statistics_view(request):
    """Get user statistics."""
    stats = AnalyticsService.get_user_statistics()
    return Response(stats, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_summary='Get job statistics',
    operation_description='Get job-related statistics. Admin only.',
    responses={
        200: openapi.Response('Job statistics retrieved'),
        403: 'Forbidden - Admin access required',
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def job_statistics_view(request):
    """Get job statistics."""
    stats = AnalyticsService.get_job_statistics()
    return Response(stats, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_summary='Get application statistics',
    operation_description='Get application-related statistics. Admin only.',
    responses={
        200: openapi.Response('Application statistics retrieved'),
        403: 'Forbidden - Admin access required',
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def application_statistics_view(request):
    """Get application statistics."""
    stats = AnalyticsService.get_application_statistics()
    return Response(stats, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_summary='Get user activity',
    operation_description='Get activity statistics for a specific user. Admin only.',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_QUERY,
            description='User ID (UUID) to get activity for',
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            required=True
        ),
        openapi.Parameter(
            'days',
            openapi.IN_QUERY,
            description='Number of days to look back (default: 30)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: openapi.Response('User activity retrieved'),
        403: 'Forbidden - Admin access required',
        404: 'User not found',
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_activity_view(request):
    """Get activity statistics for a specific user."""
    user_id = request.query_params.get('user_id')
    days = int(request.query_params.get('days', 30))
    
    if not user_id:
        return Response(
            {'error': 'user_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # user_id is now a UUID string, not an integer
        activity = AnalyticsService.get_user_activity(user_id, days)
        return Response(activity, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as e:
        return Response(
            {'error': f'Invalid user ID: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )