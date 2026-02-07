"""
User profile enhancement models.
"""
from django.db import models
from django.core.validators import URLValidator
from .models import User


class Skill(models.Model):
    """
    Model for user skills.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='skills',
        help_text='User who owns this skill'
    )
    name = models.CharField(
        max_length=100,
        db_index=True,
        help_text='Skill name (e.g., Python, JavaScript)'
    )
    level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        default='intermediate',
        help_text='Skill proficiency level'
    )
    years_of_experience = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Years of experience with this skill'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_skills'
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        unique_together = [['user', 'name']]
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'name']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.name} ({self.level})"


class Education(models.Model):
    """
    Model for user education history.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='education',
        help_text='User who has this education'
    )
    institution = models.CharField(
        max_length=200,
        help_text='School/University name'
    )
    degree = models.CharField(
        max_length=100,
        help_text='Degree type (e.g., Bachelor of Science, Master of Arts)'
    )
    field_of_study = models.CharField(
        max_length=100,
        help_text='Field of study (e.g., Computer Science, Business)'
    )
    start_date = models.DateField(
        help_text='Education start date'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Education end date (null if ongoing)'
    )
    is_current = models.BooleanField(
        default=False,
        help_text='Whether this education is ongoing'
    )
    description = models.TextField(
        blank=True,
        help_text='Additional details (honors, achievements, etc.)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_education'
        verbose_name = 'Education'
        verbose_name_plural = 'Education'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', '-start_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.degree} in {self.field_of_study}"
    
    def clean(self):
        """Validate education dates."""
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError('End date must be after start date.')
        if self.is_current and self.end_date:
            raise ValidationError('Current education cannot have an end date.')


class WorkHistory(models.Model):
    """
    Model for user work experience history.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='work_history',
        help_text='User who has this work experience'
    )
    company = models.CharField(
        max_length=200,
        help_text='Company name'
    )
    position = models.CharField(
        max_length=200,
        help_text='Job title/position'
    )
    start_date = models.DateField(
        help_text='Employment start date'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Employment end date (null if current job)'
    )
    is_current = models.BooleanField(
        default=False,
        help_text='Whether this is the current job'
    )
    description = models.TextField(
        blank=True,
        help_text='Job description and responsibilities'
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text='Job location'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_work_history'
        verbose_name = 'Work History'
        verbose_name_plural = 'Work History'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', '-start_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.position} at {self.company}"
    
    def clean(self):
        """Validate work history dates."""
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError('End date must be after start date.')
        if self.is_current and self.end_date:
            raise ValidationError('Current job cannot have an end date.')


class Portfolio(models.Model):
    """
    Model for user portfolio/projects.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='portfolio',
        help_text='User who owns this portfolio item'
    )
    title = models.CharField(
        max_length=200,
        help_text='Project title'
    )
    description = models.TextField(
        help_text='Project description'
    )
    url = models.URLField(
        blank=True,
        help_text='Project URL (GitHub, website, etc.)'
    )
    technologies = models.CharField(
        max_length=500,
        blank=True,
        help_text='Technologies used (comma-separated)'
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text='Project start date'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Project end date'
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Whether this is a featured project'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_portfolio'
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolio'
        ordering = ['-is_featured', '-start_date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-is_featured']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"


class SocialLink(models.Model):
    """
    Model for user social media links.
    """
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('website', 'Personal Website'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_links',
        help_text='User who owns this social link'
    )
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        help_text='Social media platform'
    )
    url = models.URLField(
        help_text='Social media profile URL'
    )
    is_public = models.BooleanField(
        default=True,
        help_text='Whether this link is publicly visible'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_social_links'
        verbose_name = 'Social Link'
        verbose_name_plural = 'Social Links'
        unique_together = [['user', 'platform']]
        ordering = ['platform']
        indexes = [
            models.Index(fields=['user', 'platform']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.get_platform_display()}"


class UserPreferences(models.Model):
    """
    Model for user preferences and settings.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences',
        help_text='User preferences'
    )
    
    # Email notification preferences
    email_job_alerts = models.BooleanField(
        default=True,
        help_text='Receive email notifications for job alerts'
    )
    email_application_updates = models.BooleanField(
        default=True,
        help_text='Receive email notifications for application updates'
    )
    email_new_jobs = models.BooleanField(
        default=False,
        help_text='Receive email notifications for new jobs matching saved searches'
    )
    email_newsletter = models.BooleanField(
        default=False,
        help_text='Receive newsletter emails'
    )
    
    # Job alert preferences
    alert_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='daily',
        help_text='Frequency of job alert emails'
    )
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('employers', 'Employers Only'),
            ('private', 'Private'),
        ],
        default='employers',
        help_text='Profile visibility level'
    )
    show_email = models.BooleanField(
        default=False,
        help_text='Show email address on profile'
    )
    show_phone = models.BooleanField(
        default=False,
        help_text='Show phone number on profile'
    )
    show_location = models.BooleanField(
        default=True,
        help_text='Show location on profile'
    )
    
    # Resume settings
    resume_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('employers', 'Employers Only'),
            ('private', 'Private'),
        ],
        default='employers',
        help_text='Resume visibility level'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"


class SavedJob(models.Model):
    """
    Model for saved jobs/bookmarks.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_jobs',
        help_text='User who saved this job'
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='saved_by_users',
        help_text='Saved job'
    )
    notes = models.TextField(
        blank=True,
        help_text='Personal notes about this job'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'saved_jobs'
        verbose_name = 'Saved Job'
        verbose_name_plural = 'Saved Jobs'
        unique_together = [['user', 'job']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} saved: {self.job.title}"
