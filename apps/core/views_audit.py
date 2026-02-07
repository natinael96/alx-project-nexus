"""
Views for audit logging and change history.
"""
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status, viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.contenttypes.models import ContentType
from apps.core.models_audit import AuditLog, ChangeHistory
from apps.core.audit_service import AuditService
from apps.core.serializers_audit import AuditLogSerializer, ChangeHistorySerializer
import logging

logger = logging.getLogger(__name__)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs (Admin only).
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Return audit logs with optional filtering."""
        queryset = AuditLog.objects.select_related('user', 'content_type')
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by content type
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type__model=content_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')


class ChangeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing change history (Admin only).
    """
    serializer_class = ChangeHistorySerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Return change history with optional filtering."""
        queryset = ChangeHistory.objects.select_related('changed_by', 'content_type')
        
        # Filter by content type and object ID
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        if content_type and object_id:
            try:
                ct = ContentType.objects.get(model=content_type)
                queryset = queryset.filter(content_type=ct, object_id=object_id)
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(changed_by_id=user_id)
        
        # Filter by field
        field_name = self.request.query_params.get('field_name')
        if field_name:
            queryset = queryset.filter(field_name=field_name)
        
        return queryset.order_by('-created_at')


@swagger_auto_schema(
    method='get',
    operation_summary='Get object change history',
    operation_description='Get change history for a specific object. Admin only.',
    manual_parameters=[
        openapi.Parameter(
            'content_type',
            openapi.IN_QUERY,
            description='Content type (e.g., job, application, user)',
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'object_id',
            openapi.IN_QUERY,
            description='Object ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        200: ChangeHistorySerializer(many=True),
        403: 'Forbidden - Admin access required',
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def object_history(request):
    """Get change history for a specific object."""
    content_type = request.query_params.get('content_type')
    object_id = request.query_params.get('object_id')
    
    if not content_type or not object_id:
        return Response(
            {'error': 'content_type and object_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        ct = ContentType.objects.get(model=content_type)
        history = ChangeHistory.objects.filter(
            content_type=ct,
            object_id=object_id
        ).order_by('-created_at')
        
        serializer = ChangeHistorySerializer(history, many=True)
        return Response(serializer.data)
    except ContentType.DoesNotExist:
        return Response(
            {'error': 'Invalid content type'},
            status=status.HTTP_400_BAD_REQUEST
        )
