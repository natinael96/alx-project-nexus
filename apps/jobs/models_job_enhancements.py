"""
Job enhancement models.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from .models import Job
from apps.accounts.models import User


class JobView(models.Model):
    """
    Model to track job views for analytics.
    """
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='views',
        help_text='Job that was viewed'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_views',
        help_text='User who viewed the job (null for anonymous)'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the viewer'
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text='User agent string'
    )
    referrer = models.URLField(
        blank=True,
        help_text='Referrer URL'
    )
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'job_views'
        verbose_name = 'Job View'
        verbose_name_plural = 'Job Views'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['job', '-viewed_at']),
            models.Index(fields=['user', '-viewed_at']),
            models.Index(fields=['-viewed_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{self.job.title} viewed by {user_str}"


class JobShare(models.Model):
    """
    Model to track job shares.
    """
    SHARE_METHOD_CHOICES = [
        ('email', 'Email'),
        ('link', 'Link'),
        ('social', 'Social Media'),
        ('other', 'Other'),
    ]
    
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='shares',
        help_text='Job that was shared'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_shares',
        help_text='User who shared the job'
    )
    method = models.CharField(
        max_length=20,
        choices=SHARE_METHOD_CHOICES,
        help_text='Sharing method'
    )
    shared_with = models.CharField(
        max_length=255,
        blank=True,
        help_text='Email or identifier of who it was shared with'
    )
    shared_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'job_shares'
        verbose_name = 'Job Share'
        verbose_name_plural = 'Job Shares'
        ordering = ['-shared_at']
        indexes = [
            models.Index(fields=['job', '-shared_at']),
        ]
    
    def __str__(self):
        return f"{self.job.title} shared via {self.get_method_display()}"


class JobRecommendation(models.Model):
    """
    Model for job recommendations to users.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_recommendations',
        help_text='User who receives the recommendation'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='recommendations',
        help_text='Recommended job'
    )
    score = models.FloatField(
        default=0.0,
        help_text='Recommendation score (0.0 to 1.0)'
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        help_text='Reason for recommendation'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    viewed = models.BooleanField(
        default=False,
        help_text='Whether user has viewed this recommendation'
    )
    clicked = models.BooleanField(
        default=False,
        help_text='Whether user clicked on this recommendation'
    )
    
    class Meta:
        db_table = 'job_recommendations'
        verbose_name = 'Job Recommendation'
        verbose_name_plural = 'Job Recommendations'
        unique_together = [['user', 'job']]
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['job', '-score']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.job.title} (score: {self.score})"


class JobAnalytics(models.Model):
    """
    Model for job performance analytics.
    """
    job = models.OneToOneField(
        Job,
        on_delete=models.CASCADE,
        related_name='analytics',
        help_text='Job analytics'
    )
    total_views = models.PositiveIntegerField(
        default=0,
        help_text='Total number of views'
    )
    unique_views = models.PositiveIntegerField(
        default=0,
        help_text='Number of unique viewers'
    )
    total_applications = models.PositiveIntegerField(
        default=0,
        help_text='Total number of applications'
    )
    shares_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of times job was shared'
    )
    saved_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of times job was saved'
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'job_analytics'
        verbose_name = 'Job Analytics'
        verbose_name_plural = 'Job Analytics'
    
    def __str__(self):
        return f"Analytics for {self.job.title}"
    
    def update_metrics(self):
        """Update analytics metrics from related models."""
        self.total_views = self.job.views.count()
        self.unique_views = self.job.views.values('user', 'ip_address').distinct().count()
        self.total_applications = self.job.applications.count()
        self.shares_count = self.job.shares.count()
        self.saved_count = self.job.saved_by_users.count()
        self.save()


class ApplicationSource(models.Model):
    """
    Model to track where applications come from.
    """
    application = models.OneToOneField(
        'jobs.Application',
        on_delete=models.CASCADE,
        related_name='source',
        help_text='Application source tracking'
    )
    source_type = models.CharField(
        max_length=50,
        choices=[
            ('direct', 'Direct Application'),
            ('referral', 'Referral'),
            ('job_board', 'Job Board'),
            ('social_media', 'Social Media'),
            ('email', 'Email Campaign'),
            ('other', 'Other'),
        ],
        default='direct',
        help_text='Source type'
    )
    referrer_url = models.URLField(
        blank=True,
        help_text='Referrer URL if applicable'
    )
    campaign = models.CharField(
        max_length=100,
        blank=True,
        help_text='Marketing campaign identifier'
    )
    utm_source = models.CharField(
        max_length=100,
        blank=True,
        help_text='UTM source parameter'
    )
    utm_medium = models.CharField(
        max_length=100,
        blank=True,
        help_text='UTM medium parameter'
    )
    utm_campaign = models.CharField(
        max_length=100,
        blank=True,
        help_text='UTM campaign parameter'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'application_sources'
        verbose_name = 'Application Source'
        verbose_name_plural = 'Application Sources'
        indexes = [
            models.Index(fields=['source_type']),
            models.Index(fields=['utm_source', 'utm_medium']),
        ]
    
    def __str__(self):
        return f"{self.application.job.title} - {self.get_source_type_display()}"
