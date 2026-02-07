"""
Application enhancement models.
"""
from django.db import models
from django.utils import timezone
from .models import Application, Job
from apps.accounts.models import User
from apps.core.models_base import UUIDModel


class ApplicationNote(UUIDModel):
    """
    Model for employer notes and ratings on applications.
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='application_notes',
        help_text='Application this note belongs to'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='application_notes',
        help_text='User who wrote the note'
    )
    note = models.TextField(
        help_text='Note content'
    )
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text='Rating (1-5 stars)'
    )
    is_internal = models.BooleanField(
        default=True,
        help_text='Whether this note is internal (not visible to applicant)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'application_notes'
        verbose_name = 'Application Note'
        verbose_name_plural = 'Application Notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['application', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"Note on {self.application.job.title} by {self.author.username}"


class ApplicationStatusHistory(UUIDModel):
    """
    Model to track application status changes over time.
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history',
        help_text='Application this history belongs to'
    )
    old_status = models.CharField(
        max_length=20,
        choices=Application.STATUS_CHOICES,
        null=True,
        blank=True,
        help_text='Previous status'
    )
    new_status = models.CharField(
        max_length=20,
        choices=Application.STATUS_CHOICES,
        help_text='New status'
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='application_status_changes',
        help_text='User who changed the status'
    )
    reason = models.TextField(
        blank=True,
        help_text='Reason for status change'
    )
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'application_status_history'
        verbose_name = 'Application Status History'
        verbose_name_plural = 'Application Status Histories'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['application', '-changed_at']),
            models.Index(fields=['changed_by', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.application.job.title}: {self.old_status} → {self.new_status}"


class ScreeningQuestion(UUIDModel):
    """
    Model for job screening questions.
    """
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text'),
        ('multiple_choice', 'Multiple Choice'),
        ('yes_no', 'Yes/No'),
        ('number', 'Number'),
        ('date', 'Date'),
    ]
    
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='screening_questions',
        help_text='Job this question belongs to'
    )
    question = models.TextField(
        help_text='Question text'
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='text',
        help_text='Type of question'
    )
    is_required = models.BooleanField(
        default=True,
        help_text='Whether this question is required'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order'
    )
    options = models.JSONField(
        default=list,
        blank=True,
        help_text='Options for multiple choice questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'screening_questions'
        verbose_name = 'Screening Question'
        verbose_name_plural = 'Screening Questions'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['job', 'order']),
        ]
    
    def __str__(self):
        return f"{self.job.title}: {self.question[:50]}"


class ScreeningAnswer(UUIDModel):
    """
    Model for answers to screening questions.
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='screening_answers',
        help_text='Application this answer belongs to'
    )
    question = models.ForeignKey(
        ScreeningQuestion,
        on_delete=models.CASCADE,
        related_name='answers',
        help_text='Question being answered'
    )
    answer = models.TextField(
        help_text='Answer text'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'screening_answers'
        verbose_name = 'Screening Answer'
        verbose_name_plural = 'Screening Answers'
        unique_together = [['application', 'question']]
        indexes = [
            models.Index(fields=['application', 'question']),
        ]
    
    def __str__(self):
        return f"Answer to {self.question.question[:50]}"


class ApplicationStage(UUIDModel):
    """
    Model for multi-stage application process.
    """
    STAGE_TYPE_CHOICES = [
        ('application', 'Application'),
        ('screening', 'Screening'),
        ('interview', 'Interview'),
        ('assessment', 'Assessment'),
        ('offer', 'Offer'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='stages',
        help_text='Application this stage belongs to'
    )
    stage_type = models.CharField(
        max_length=20,
        choices=STAGE_TYPE_CHOICES,
        help_text='Type of stage'
    )
    stage_name = models.CharField(
        max_length=100,
        help_text='Custom stage name'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Stage order'
    )
    is_completed = models.BooleanField(
        default=False,
        help_text='Whether this stage is completed'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this stage was completed'
    )
    notes = models.TextField(
        blank=True,
        help_text='Stage notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'application_stages'
        verbose_name = 'Application Stage'
        verbose_name_plural = 'Application Stages'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['application', 'order']),
            models.Index(fields=['application', 'is_completed']),
        ]
    
    def __str__(self):
        return f"{self.application.job.title}: {self.stage_name}"


class Interview(UUIDModel):
    """
    Model for interview scheduling.
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interviews',
        help_text='Application this interview is for'
    )
    scheduled_at = models.DateTimeField(
        help_text='Interview scheduled date and time'
    )
    duration = models.PositiveIntegerField(
        default=60,
        help_text='Interview duration in minutes'
    )
    interview_type = models.CharField(
        max_length=20,
        choices=[
            ('phone', 'Phone'),
            ('video', 'Video'),
            ('in_person', 'In Person'),
            ('other', 'Other'),
        ],
        default='video',
        help_text='Type of interview'
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text='Interview location (for in-person)'
    )
    video_link = models.URLField(
        blank=True,
        help_text='Video call link (for video interviews)'
    )
    interviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interviews',
        help_text='Interviewer'
    )
    notes = models.TextField(
        blank=True,
        help_text='Interview notes'
    )
    is_confirmed = models.BooleanField(
        default=False,
        help_text='Whether interview is confirmed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'interviews'
        verbose_name = 'Interview'
        verbose_name_plural = 'Interviews'
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['application', 'scheduled_at']),
            models.Index(fields=['interviewer', 'scheduled_at']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"Interview for {self.application.job.title} on {self.scheduled_at}"


class ApplicationScore(UUIDModel):
    """
    Model for application scoring/ranking.
    """
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='score',
        help_text='Application score'
    )
    overall_score = models.FloatField(
        default=0.0,
        help_text='Overall score (0.0 to 100.0)'
    )
    experience_score = models.FloatField(
        default=0.0,
        help_text='Experience score'
    )
    skills_score = models.FloatField(
        default=0.0,
        help_text='Skills score'
    )
    education_score = models.FloatField(
        default=0.0,
        help_text='Education score'
    )
    screening_score = models.FloatField(
        default=0.0,
        help_text='Screening questions score'
    )
    notes = models.TextField(
        blank=True,
        help_text='Scoring notes'
    )
    scored_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scored_applications',
        help_text='User who scored this application'
    )
    scored_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'application_scores'
        verbose_name = 'Application Score'
        verbose_name_plural = 'Application Scores'
        ordering = ['-overall_score']
        indexes = [
            models.Index(fields=['-overall_score']),
            models.Index(fields=['scored_by', '-scored_at']),
        ]
    
    def __str__(self):
        return f"Score {self.overall_score} for {self.application.job.title}"


class ApplicationTemplate(UUIDModel):
    """
    Model for application templates.
    """
    employer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='application_templates',
        help_text='Employer who owns this template'
    )
    name = models.CharField(
        max_length=100,
        help_text='Template name'
    )
    description = models.TextField(
        blank=True,
        help_text='Template description'
    )
    default_notes = models.TextField(
        blank=True,
        help_text='Default notes for applications using this template'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this template is active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'application_templates'
        verbose_name = 'Application Template'
        verbose_name_plural = 'Application Templates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employer', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} by {self.employer.username}"
