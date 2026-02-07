"""
Service for exporting data to CSV, JSON, and other formats.
"""
import csv
import json
import logging
from io import StringIO, BytesIO
from typing import List, Dict, Any
from django.http import HttpResponse
from django.db.models import Model, QuerySet
from django.core.serializers import serialize

logger = logging.getLogger(__name__)


class ExportService:
    """
    Service for exporting data to various formats.
    """
    
    @staticmethod
    def export_to_csv(queryset: QuerySet, fields: List[str], filename: str = 'export.csv') -> HttpResponse:
        """
        Export queryset to CSV format.
        
        Args:
            queryset: Django queryset to export
            fields: List of field names to export
            filename: Output filename
            
        Returns:
            HttpResponse with CSV file
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow(fields)
        
        # Write data rows
        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field, '')
                # Handle related objects
                if hasattr(value, '__str__'):
                    value = str(value)
                row.append(value)
            writer.writerow(row)
        
        return response
    
    @staticmethod
    def export_to_json(queryset: QuerySet, fields: List[str] = None, filename: str = 'export.json') -> HttpResponse:
        """
        Export queryset to JSON format.
        
        Args:
            queryset: Django queryset to export
            fields: List of field names to export (None for all)
            filename: Output filename
            
        Returns:
            HttpResponse with JSON file
        """
        if fields:
            data = []
            for obj in queryset:
                item = {}
                for field in fields:
                    value = getattr(obj, field, None)
                    # Handle dates and related objects
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    elif hasattr(value, '__str__'):
                        value = str(value)
                    item[field] = value
                data.append(item)
        else:
            # Use Django's serializer for full object serialization
            data = json.loads(serialize('json', queryset))
        
        response = HttpResponse(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @staticmethod
    def export_jobs(queryset, format: str = 'csv') -> HttpResponse:
        """Export jobs to specified format."""
        fields = [
            'id', 'title', 'description', 'category', 'employer',
            'location', 'job_type', 'salary_min', 'salary_max',
            'status', 'is_featured', 'views_count', 'created_at'
        ]
        
        if format == 'json':
            return ExportService.export_to_json(queryset, fields, 'jobs_export.json')
        else:
            return ExportService.export_to_csv(queryset, fields, 'jobs_export.csv')
    
    @staticmethod
    def export_applications(queryset, format: str = 'csv') -> HttpResponse:
        """Export applications to specified format."""
        fields = [
            'id', 'job', 'applicant', 'status', 'applied_at',
            'reviewed_at', 'is_withdrawn'
        ]
        
        if format == 'json':
            return ExportService.export_to_json(queryset, fields, 'applications_export.json')
        else:
            return ExportService.export_to_csv(queryset, fields, 'applications_export.csv')
    
    @staticmethod
    def export_users(queryset, format: str = 'csv') -> HttpResponse:
        """Export users to specified format."""
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'is_active', 'date_joined'
        ]
        
        if format == 'json':
            return ExportService.export_to_json(queryset, fields, 'users_export.json')
        else:
            return ExportService.export_to_csv(queryset, fields, 'users_export.csv')
