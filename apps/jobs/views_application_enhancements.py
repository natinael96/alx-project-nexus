"""
Views for application enhancement features.
"""
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from .models import Application
from .models_application_enhancements import (
    ApplicationNote, ApplicationStatusHistory, ScreeningQuestion,
    ScreeningAnswer, ApplicationStage, Interview, ApplicationScore,
    ApplicationTemplate
)
from .serializers_application_enhancements import (
    ApplicationNoteSerializer, ApplicationStatusHistorySerializer,
    ScreeningQuestionSerializer, ScreeningAnswerSerializer,
    ApplicationStageSerializer, InterviewSerializer,
    ApplicationScoreSerializer, ApplicationTemplateSerializer
)
from apps.accounts.permissions import IsEmployerOrAdmin
from .permissions import IsJobOwnerOrAdmin
import logging

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='post',
    operation_summary='Withdraw application',
    operation_description='Withdraw an application. Only the applicant can withdraw their own application.',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'reason': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: 'Application withdrawn successfully',
        400: 'Bad Request',
        403: 'Forbidden',
        404: 'Application not found',
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_application(request, application_id):
    """Withdraw an application."""
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response(
            {'error': 'Application not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if application.applicant != request.user:
        return Response(
            {'error': 'You can only withdraw your own applications'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if application.is_withdrawn:
        return Response(
            {'error': 'Application is already withdrawn'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Withdraw application
    application.is_withdrawn = True
    application.withdrawn_at = timezone.now()
    application.withdrawal_reason = request.data.get('reason', '')
    application.save()
    
    # Create status history
    ApplicationStatusHistory.objects.create(
        application=application,
        old_status=application.status,
        new_status='withdrawn',
        changed_by=request.user,
        reason=application.withdrawal_reason
    )
    
    return Response({
        'message': 'Application withdrawn successfully',
        'application_id': application.id
    })


class ApplicationNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing application notes.
    """
    serializer_class = ApplicationNoteSerializer
    permission_classes = [IsEmployerOrAdmin]
    
    def get_queryset(self):
        """Return notes for applications the user can access."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return ApplicationNote.objects.none()
        if not self.request.user.is_authenticated:
            return ApplicationNote.objects.none()
        
        if self.request.user.is_admin:
            return ApplicationNote.objects.all()
        # Employers can only see notes for their jobs
        return ApplicationNote.objects.filter(
            application__job__employer=self.request.user
        )
    
    def perform_create(self, serializer):
        """Set the author when creating a note."""
        serializer.save(author=self.request.user)


class ApplicationStatusHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing application status history.
    """
    serializer_class = ApplicationStatusHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return status history for applications the user can access."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return ApplicationStatusHistory.objects.none()
        if not self.request.user.is_authenticated:
            return ApplicationStatusHistory.objects.none()
        
        if self.request.user.is_admin:
            return ApplicationStatusHistory.objects.all()
        elif self.request.user.is_employer:
            return ApplicationStatusHistory.objects.filter(
                application__job__employer=self.request.user
            )
        else:
            return ApplicationStatusHistory.objects.filter(
                application__applicant=self.request.user
            )


class ScreeningQuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing screening questions.
    """
    serializer_class = ScreeningQuestionSerializer
    permission_classes = [IsEmployerOrAdmin]
    
    def get_queryset(self):
        """Return screening questions for jobs the user can access."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return ScreeningQuestion.objects.none()
        if not self.request or not self.request.user.is_authenticated:
            return ScreeningQuestion.objects.none()
        
        job_id = self.request.query_params.get('job_id')
        queryset = ScreeningQuestion.objects.all()
        
        if not self.request.user.is_admin:
            queryset = queryset.filter(job__employer=self.request.user)
        
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        return queryset.order_by('order', 'created_at')
    
    def perform_create(self, serializer):
        """Validate job ownership."""
        job = serializer.validated_data.get('job')
        if not self.request.user.is_admin and job.employer != self.request.user:
            raise PermissionError('You can only add screening questions to your own jobs.')
        serializer.save()


class ScreeningAnswerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing screening answers.
    """
    serializer_class = ScreeningAnswerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return answers for applications the user can access."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return ScreeningAnswer.objects.none()
        if not self.request.user.is_authenticated:
            return ScreeningAnswer.objects.none()
        
        if self.request.user.is_admin or self.request.user.is_employer:
            return ScreeningAnswer.objects.filter(
                application__job__employer=self.request.user
            )
        return ScreeningAnswer.objects.filter(
            application__applicant=self.request.user
        )
    
    def perform_create(self, serializer):
        """Validate application ownership."""
        application = serializer.validated_data.get('application')
        if application.applicant != self.request.user:
            raise PermissionError('You can only answer questions for your own applications.')


class ApplicationStageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing application stages.
    """
    serializer_class = ApplicationStageSerializer
    permission_classes = [IsEmployerOrAdmin]
    
    def get_queryset(self):
        """Return stages for applications the user can access."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return ApplicationStage.objects.none()
        
        application_id = self.request.query_params.get('application_id')
        queryset = ApplicationStage.objects.all()
        
        if self.request.user.is_authenticated and not self.request.user.is_admin:
            queryset = queryset.filter(application__job__employer=self.request.user)
        
        if application_id:
            queryset = queryset.filter(application_id=application_id)
        
        return queryset.order_by('order', 'created_at')


class InterviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing interviews.
    """
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return interviews the user can access."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return Interview.objects.none()
        if not self.request.user.is_authenticated:
            return Interview.objects.none()
        
        if self.request.user.is_admin:
            return Interview.objects.all()
        elif self.request.user.is_employer:
            return Interview.objects.filter(
                application__job__employer=self.request.user
            )
        else:
            return Interview.objects.filter(
                application__applicant=self.request.user
            )
    
    def perform_create(self, serializer):
        """Set interviewer if employer."""
        if self.request.user.is_employer or self.request.user.is_admin:
            serializer.save(interviewer=self.request.user)


class ApplicationScoreViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing application scores.
    """
    serializer_class = ApplicationScoreSerializer
    permission_classes = [IsEmployerOrAdmin]
    
    def get_queryset(self):
        """Return scores for applications the user can access."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return ApplicationScore.objects.none()
        if not self.request.user.is_authenticated:
            return ApplicationScore.objects.none()
        
        if self.request.user.is_admin:
            return ApplicationScore.objects.all()
        return ApplicationScore.objects.filter(
            application__job__employer=self.request.user
        )
    
    def perform_create(self, serializer):
        """Set the scorer when creating a score."""
        serializer.save(scored_by=self.request.user)


class ApplicationTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing application templates.
    """
    serializer_class = ApplicationTemplateSerializer
    permission_classes = [IsEmployerOrAdmin]
    
    def get_queryset(self):
        """Return templates for the current user."""
        # Handle schema generation (swagger/redoc)
        if getattr(self, 'swagger_fake_view', False):
            return ApplicationTemplate.objects.none()
        
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return ApplicationTemplate.objects.all()
        
        if not self.request.user.is_authenticated:
            return ApplicationTemplate.objects.none()
        
        return ApplicationTemplate.objects.filter(employer=self.request.user)
    
    def perform_create(self, serializer):
        """Set the employer when creating a template."""
        serializer.save(employer=self.request.user)
