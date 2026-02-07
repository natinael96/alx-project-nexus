"""
Views for notification system.
"""
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from apps.core.models_notifications import Notification, NotificationPreference
from apps.core.serializers_notifications import NotificationSerializer, NotificationPreferenceSerializer
from apps.core.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's notifications."""
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Filter by notification type
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-created_at')
    
    @swagger_auto_schema(
        method='post',
        operation_summary='Mark notification as read',
        operation_description='Mark a specific notification as read.',
        responses={
            200: 'Notification marked as read',
            404: 'Notification not found',
        }
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='post',
        operation_summary='Mark all notifications as read',
        operation_description='Mark all unread notifications as read for the current user.',
        responses={
            200: openapi.Response(
                description='Notifications marked as read',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
        }
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        count = NotificationService.mark_all_as_read(request.user)
        return Response({
            'message': f'Marked {count} notifications as read',
            'count': count
        })
    
    @swagger_auto_schema(
        method='get',
        operation_summary='Get unread count',
        operation_description='Get count of unread notifications.',
        responses={
            200: openapi.Response(
                description='Unread notification count',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'unread_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
        }
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count."""
        count = NotificationService.get_unread_count(request.user)
        return Response({'unread_count': count})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification preferences.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's preferences."""
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create preferences for the user."""
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences
    
    def perform_create(self, serializer):
        """Set the user when creating preferences."""
        serializer.save(user=self.request.user)


@swagger_auto_schema(
    method='get',
    operation_summary='Get notification summary',
    operation_description='Get summary of notifications including unread count and recent notifications.',
    responses={
        200: 'Notification summary',
        401: 'Unauthorized',
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_summary(request):
    """Get notification summary."""
    unread_count = NotificationService.get_unread_count(request.user)
    
    # Get recent notifications (last 10)
    recent_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    serializer = NotificationSerializer(recent_notifications, many=True)
    
    return Response({
        'unread_count': unread_count,
        'recent_notifications': serializer.data
    })
