"""
Search-related models for advanced search features.
"""
from django.db import models
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from apps.accounts.models import User


class SearchHistory(models.Model):
    """
    Model to track user search history.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='search_history',
        null=True,
        blank=True,
        help_text='User who performed the search (null for anonymous)'
    )
    search_query = models.CharField(
        max_length=255,
        db_index=True,
        help_text='Search query text'
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text='Applied filters (category, location, etc.)'
    )
    result_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of results returned'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the searcher'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'search_history'
        verbose_name = 'Search History'
        verbose_name_plural = 'Search Histories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['search_query', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{user_str}: {self.search_query}"


class SavedSearch(models.Model):
    """
    Model for saved searches that users can revisit.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_searches',
        help_text='User who saved the search'
    )
    name = models.CharField(
        max_length=100,
        help_text='Name for the saved search'
    )
    search_query = models.CharField(
        max_length=255,
        help_text='Search query text'
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text='Applied filters (category, location, etc.)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this saved search is active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_searched_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this search was last executed'
    )
    
    class Meta:
        db_table = 'saved_searches'
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        ordering = ['-updated_at']
        unique_together = [['user', 'name']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.name}"


class SearchAlert(models.Model):
    """
    Model for search alerts that notify users of new matching jobs.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('immediate', 'Immediate'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='search_alerts',
        help_text='User who created the alert'
    )
    saved_search = models.ForeignKey(
        SavedSearch,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True,
        help_text='Associated saved search (optional)'
    )
    name = models.CharField(
        max_length=100,
        help_text='Name for the search alert'
    )
    search_query = models.CharField(
        max_length=255,
        help_text='Search query text'
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text='Applied filters (category, location, etc.)'
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='daily',
        help_text='How often to check for new jobs'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this alert is active'
    )
    last_notified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the user was last notified'
    )
    last_job_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID of the last job found (to avoid duplicates)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_alerts'
        verbose_name = 'Search Alert'
        verbose_name_plural = 'Search Alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['frequency', 'is_active']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.name} ({self.frequency})"


class PopularSearchTerm(models.Model):
    """
    Model to track popular search terms for analytics and suggestions.
    """
    term = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Search term'
    )
    search_count = models.PositiveIntegerField(
        default=1,
        help_text='Number of times this term has been searched'
    )
    last_searched_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text='When this term was last searched'
    )
    first_searched_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When this term was first searched'
    )
    
    class Meta:
        db_table = 'popular_search_terms'
        verbose_name = 'Popular Search Term'
        verbose_name_plural = 'Popular Search Terms'
        ordering = ['-search_count', '-last_searched_at']
        indexes = [
            models.Index(fields=['-search_count']),
            models.Index(fields=['-last_searched_at']),
        ]
    
    def __str__(self):
        return f"{self.term} ({self.search_count} searches)"
