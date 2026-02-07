"""
Admin configuration for application enhancement models.
"""
from django.contrib import admin
from .models_application_enhancements import (
    ApplicationNote, ApplicationStatusHistory, ScreeningQuestion,
    ScreeningAnswer, ApplicationStage, Interview, ApplicationScore,
    ApplicationTemplate
)


@admin.register(ApplicationNote)
class ApplicationNoteAdmin(admin.ModelAdmin):
    """
    Admin interface for ApplicationNote model.
    """
    list_display = ('application', 'author', 'rating', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'rating', 'created_at')
    search_fields = ('application__job__title', 'author__username', 'note')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('application', 'author', 'application__job')


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for ApplicationStatusHistory model.
    """
    list_display = ('application', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = ('application__job__title', 'application__applicant__username', 'reason')
    readonly_fields = ('changed_at',)
    date_hierarchy = 'changed_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('application', 'changed_by', 'application__job')


@admin.register(ScreeningQuestion)
class ScreeningQuestionAdmin(admin.ModelAdmin):
    """
    Admin interface for ScreeningQuestion model.
    """
    list_display = ('job', 'question', 'question_type', 'is_required', 'order', 'created_at')
    list_filter = ('question_type', 'is_required', 'created_at')
    search_fields = ('job__title', 'question')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('job')


@admin.register(ScreeningAnswer)
class ScreeningAnswerAdmin(admin.ModelAdmin):
    """
    Admin interface for ScreeningAnswer model.
    """
    list_display = ('application', 'question', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('application__job__title', 'question__question', 'answer')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('application', 'question', 'application__job')


@admin.register(ApplicationStage)
class ApplicationStageAdmin(admin.ModelAdmin):
    """
    Admin interface for ApplicationStage model.
    """
    list_display = ('application', 'stage_type', 'stage_name', 'order', 'is_completed', 'completed_at')
    list_filter = ('stage_type', 'is_completed', 'created_at')
    search_fields = ('application__job__title', 'stage_name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('application', 'application__job')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    """
    Admin interface for Interview model.
    """
    list_display = ('application', 'scheduled_at', 'interview_type', 'interviewer', 'is_confirmed', 'created_at')
    list_filter = ('interview_type', 'is_confirmed', 'scheduled_at', 'created_at')
    search_fields = ('application__job__title', 'application__applicant__username', 'interviewer__username', 'location')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'scheduled_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('application', 'interviewer', 'application__job')


@admin.register(ApplicationScore)
class ApplicationScoreAdmin(admin.ModelAdmin):
    """
    Admin interface for ApplicationScore model.
    """
    list_display = ('application', 'overall_score', 'experience_score', 'skills_score', 'scored_by', 'scored_at')
    list_filter = ('scored_at',)
    search_fields = ('application__job__title', 'application__applicant__username', 'scored_by__username')
    readonly_fields = ('scored_at', 'updated_at')
    date_hierarchy = 'scored_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('application', 'scored_by', 'application__job')


@admin.register(ApplicationTemplate)
class ApplicationTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for ApplicationTemplate model.
    """
    list_display = ('name', 'employer', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'employer__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('employer')
