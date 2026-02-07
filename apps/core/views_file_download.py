"""
Secure file download views with access control.
"""
from django.http import Http404, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.jobs.models import Application
from apps.accounts.models import User
from apps.core.file_management import FileAccessControl
from apps.core.storage import storage_manager
import logging

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='get',
    operation_summary='Download resume',
    operation_description='Download a resume file from an application. Access is restricted: Applicants can download their own resumes, Employers can download resumes for their jobs, Admins can download all resumes.',
    manual_parameters=[
        openapi.Parameter(
            'application_id',
            openapi.IN_PATH,
            description='Application ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'signed',
            openapi.IN_QUERY,
            description='Use signed URL (optional, for direct access)',
            type=openapi.TYPE_BOOLEAN,
            required=False
        ),
    ],
    responses={
        200: 'File download',
        401: 'Unauthorized',
        403: 'Forbidden - Access denied',
        404: 'Application or file not found',
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_resume(request, application_id):
    """
    Download a resume file with access control.
    """
    try:
        application = Application.objects.select_related('job', 'applicant', 'job__employer').get(
            id=application_id
        )
    except Application.DoesNotExist:
        return Response(
            {'error': 'Application not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check access permission
    if not FileAccessControl.can_access_resume(request.user, application):
        return Response(
            {'error': 'You do not have permission to access this file'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if file exists
    if not application.resume:
        return Response(
            {'error': 'Resume file not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        # Generate signed URL if requested
        use_signed = request.query_params.get('signed', 'false').lower() == 'true'
        
        if use_signed:
            # Return signed URL for direct access
            signed_url = storage_manager.generate_signed_url(
                str(application.resume),
                expiration=3600  # 1 hour
            )
            return Response({
                'url': signed_url,
                'expires_in': 3600,
            })
        else:
            # Stream file directly
            file_path = str(application.resume)
            
            # Get file from storage
            if storage_manager.exists(file_path):
                # For local storage, use FileResponse
                from django.core.files.storage import default_storage
                file = default_storage.open(file_path, 'rb')
                response = FileResponse(
                    file,
                    content_type='application/pdf',
                    as_attachment=True,
                    filename=os.path.basename(file_path)
                )
                return response
            else:
                # For cloud storage, redirect to signed URL
                signed_url = storage_manager.generate_signed_url(file_path, expiration=3600)
                from django.shortcuts import redirect
                return redirect(signed_url)
    
    except Exception as e:
        logger.error(f"Error downloading resume: {e}")
        return Response(
            {'error': 'Failed to download file'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    operation_summary='Download profile picture',
    operation_description='Download a user profile picture. Users can download their own profile pictures, and profile pictures are generally public.',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_PATH,
            description='User ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        200: 'Image file download',
        401: 'Unauthorized',
        403: 'Forbidden - Access denied',
        404: 'User or file not found',
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_profile_picture(request, user_id):
    """
    Download a profile picture with access control.
    """
    try:
        profile_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check access permission
    if not FileAccessControl.can_access_profile_picture(request.user, profile_user):
        return Response(
            {'error': 'You do not have permission to access this file'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if file exists
    if not profile_user.profile_picture:
        return Response(
            {'error': 'Profile picture not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        file_path = str(profile_user.profile_picture)
        
        # Get file from storage
        if storage_manager.exists(file_path):
            # Try to get file from default storage (local)
            try:
                from django.core.files.storage import default_storage
                if default_storage.exists(file_path):
                    file = default_storage.open(file_path, 'rb')
                    response = FileResponse(
                        file,
                        content_type='image/jpeg',
                        filename=os.path.basename(file_path)
                    )
                    return response
            except Exception:
                pass
            
            # For cloud storage, redirect to signed URL
            signed_url = storage_manager.generate_signed_url(file_path, expiration=3600)
            from django.shortcuts import redirect
            return redirect(signed_url)
        else:
            return Response(
                {'error': 'File not found in storage'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    except Exception as e:
        logger.error(f"Error downloading profile picture: {e}")
        return Response(
            {'error': 'Failed to download file'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
