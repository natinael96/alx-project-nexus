"""
Admin configuration for search-related models.
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.jobs.models_search import SearchHistory, SavedSearch, SearchAlert, PopularSearchTerm


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for SearchHistory model.
    """
    list_display = ('search_query', 'user_display', 'result_count', 'created_at', 'ip_address')
    list_filter = ('created_at', 'user')
    search_fields = ('search_query', 'user__username', 'user__email')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def user_display(self, obj):
        """Display user or Anonymous."""
        if obj.user:
            return obj.user.username
        return 'Anonymous'
    user_display.short_description = 'User'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    """
    Admin interface for SavedSearch model.
    """
    list_display = ('name', 'user', 'search_query', 'is_active', 'created_at', 'last_searched_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'search_query', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'last_searched_at')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user')


@admin.register(SearchAlert)
class SearchAlertAdmin(admin.ModelAdmin):
    """
    Admin interface for SearchAlert model.
    """
    list_display = ('name', 'user', 'frequency', 'is_active', 'last_notified_at', 'created_at')
    list_filter = ('frequency', 'is_active', 'created_at')
    search_fields = ('name', 'search_query', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'last_notified_at')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset().select_related('user', 'saved_search')


@admin.register(PopularSearchTerm)
class PopularSearchTermAdmin(admin.ModelAdmin):
    """
    Admin interface for PopularSearchTerm model.
    """
    list_display = ('term', 'search_count', 'first_searched_at', 'last_searched_at')
    list_filter = ('first_searched_at', 'last_searched_at')
    search_fields = ('term',)
    readonly_fields = ('first_searched_at', 'last_searched_at')
    date_hierarchy = 'last_searched_at'
    ordering = ('-search_count', '-last_searched_at')
