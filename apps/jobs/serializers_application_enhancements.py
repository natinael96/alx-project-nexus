"""
Serializers for application enhancement models.
"""
from rest_framework import serializers
from .models import Application
from .models_application_enhancements import (
    ApplicationNote, ApplicationStatusHistory, ScreeningQuestion,
    ScreeningAnswer, ApplicationStage, Interview, ApplicationScore,
    ApplicationTemplate
)
from apps.accounts.models import User


class ApplicationNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for ApplicationNote model.
    """
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = ApplicationNote
        fields = (
            'id', 'application', 'author', 'author_name', 'note', 'rating',
            'is_internal', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')
    
    def validate_rating(self, value):
        """Validate rating range."""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for ApplicationStatusHistory model.
    """
    old_status_display = serializers.CharField(source='get_old_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = ApplicationStatusHistory
        fields = (
            'id', 'application', 'old_status', 'old_status_display',
            'new_status', 'new_status_display', 'changed_by', 'changed_by_name',
            'reason', 'changed_at'
        )
        read_only_fields = (
            'id', 'application', 'old_status', 'old_status_display',
            'new_status', 'new_status_display', 'changed_by', 'changed_by_name',
            'reason', 'changed_at'
        )


class ScreeningQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for ScreeningQuestion model.
    """
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)
    
    class Meta:
        model = ScreeningQuestion
        fields = (
            'id', 'job', 'question', 'question_type', 'question_type_display',
            'is_required', 'order', 'options', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
    
    def validate_options(self, value):
        """Validate options for multiple choice questions."""
        if self.initial_data.get('question_type') == 'multiple_choice':
            if not value or len(value) < 2:
                raise serializers.ValidationError(
                    'Multiple choice questions must have at least 2 options.'
                )
        return value


class ScreeningAnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for ScreeningAnswer model.
    """
    question_text = serializers.CharField(source='question.question', read_only=True)
    
    class Meta:
        model = ScreeningAnswer
        fields = (
            'id', 'application', 'question', 'question_text', 'answer', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class ApplicationStageSerializer(serializers.ModelSerializer):
    """
    Serializer for ApplicationStage model.
    """
    stage_type_display = serializers.CharField(source='get_stage_type_display', read_only=True)
    
    class Meta:
        model = ApplicationStage
        fields = (
            'id', 'application', 'stage_type', 'stage_type_display',
            'stage_name', 'order', 'is_completed', 'completed_at',
            'notes', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class InterviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Interview model.
    """
    interview_type_display = serializers.CharField(source='get_interview_type_display', read_only=True)
    interviewer_name = serializers.CharField(source='interviewer.username', read_only=True, allow_null=True)
    job_title = serializers.CharField(source='application.job.title', read_only=True)
    applicant_name = serializers.CharField(source='application.applicant.username', read_only=True)
    
    class Meta:
        model = Interview
        fields = (
            'id', 'application', 'job_title', 'applicant_name',
            'scheduled_at', 'duration', 'interview_type', 'interview_type_display',
            'location', 'video_link', 'interviewer', 'interviewer_name',
            'notes', 'is_confirmed', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_scheduled_at(self, value):
        """Validate interview is scheduled in the future."""
        from django.utils import timezone
        if value and value <= timezone.now():
            raise serializers.ValidationError('Interview must be scheduled in the future.')
        return value


class ApplicationScoreSerializer(serializers.ModelSerializer):
    """
    Serializer for ApplicationScore model.
    """
    scored_by_name = serializers.CharField(source='scored_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ApplicationScore
        fields = (
            'id', 'application', 'overall_score', 'experience_score',
            'skills_score', 'education_score', 'screening_score',
            'notes', 'scored_by', 'scored_by_name', 'scored_at', 'updated_at'
        )
        read_only_fields = ('id', 'scored_by', 'scored_at', 'updated_at')
    
    def validate(self, attrs):
        """Validate score ranges."""
        score_fields = ['overall_score', 'experience_score', 'skills_score', 
                       'education_score', 'screening_score']
        for field in score_fields:
            value = attrs.get(field, 0)
            if value < 0 or value > 100:
                raise serializers.ValidationError({
                    field: f'{field} must be between 0 and 100.'
                })
        return attrs


class ApplicationTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for ApplicationTemplate model.
    """
    employer_name = serializers.CharField(source='employer.username', read_only=True)
    
    class Meta:
        model = ApplicationTemplate
        fields = (
            'id', 'employer', 'employer_name', 'name', 'description',
            'default_notes', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'employer', 'created_at', 'updated_at')
