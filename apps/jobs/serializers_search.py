"""
Serializers for search-related models.
"""
from rest_framework import serializers
from apps.jobs.models_search import SavedSearch, SearchAlert, SearchHistory, PopularSearchTerm
from apps.accounts.models import User


class SavedSearchSerializer(serializers.ModelSerializer):
    """
    Serializer for SavedSearch model.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = SavedSearch
        fields = (
            'id', 'user', 'name', 'search_query', 'filters',
            'is_active', 'created_at', 'updated_at', 'last_searched_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'last_searched_at')
    
    def validate_name(self, value):
        """Validate saved search name."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Name must be at least 3 characters long.')
        return value.strip()
    
    def validate(self, attrs):
        """Validate saved search data."""
        # Check for duplicate names for the same user
        user = self.context['request'].user
        name = attrs.get('name')
        
        if name:
            existing = SavedSearch.objects.filter(user=user, name=name)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError({
                    'name': 'You already have a saved search with this name.'
                })
        
        return attrs


class SearchAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for SearchAlert model.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    saved_search = serializers.PrimaryKeyRelatedField(
        queryset=SavedSearch.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = SearchAlert
        fields = (
            'id', 'user', 'saved_search', 'name', 'search_query', 'filters',
            'frequency', 'is_active', 'last_notified_at', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'last_notified_at', 'created_at', 'updated_at'
        )
    
    def validate_name(self, value):
        """Validate alert name."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Name must be at least 3 characters long.')
        return value.strip()
    
    def validate(self, attrs):
        """Validate alert data."""
        # Ensure either search_query or saved_search is provided
        if not attrs.get('search_query') and not attrs.get('saved_search'):
            raise serializers.ValidationError({
                'search_query': 'Either search_query or saved_search must be provided.'
            })
        
        # If saved_search is provided, use its query and filters
        if attrs.get('saved_search'):
            saved_search = attrs['saved_search']
            if saved_search.user != self.context['request'].user:
                raise serializers.ValidationError({
                    'saved_search': 'You can only use your own saved searches.'
                })
            # Use saved search's query and filters if not provided
            if not attrs.get('search_query'):
                attrs['search_query'] = saved_search.search_query
            if not attrs.get('filters'):
                attrs['filters'] = saved_search.filters
        
        return attrs


class SearchHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for SearchHistory model (read-only).
    """
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = SearchHistory
        fields = (
            'id', 'user', 'search_query', 'filters',
            'result_count', 'created_at'
        )
        read_only_fields = '__all__'


class PopularSearchTermSerializer(serializers.ModelSerializer):
    """
    Serializer for PopularSearchTerm model (read-only).
    """
    class Meta:
        model = PopularSearchTerm
        fields = (
            'id', 'term', 'search_count',
            'first_searched_at', 'last_searched_at'
        )
        read_only_fields = '__all__'
