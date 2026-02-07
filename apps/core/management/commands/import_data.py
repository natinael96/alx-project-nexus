"""
Management command for bulk data import.
"""
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
import json
import csv
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import data from CSV or JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the import file'
        )
        parser.add_argument(
            '--model',
            type=str,
            required=True,
            choices=['job', 'application', 'user', 'category'],
            help='Model to import data for'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json'],
            default='json',
            help='File format (csv or json)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually importing'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        model_name = options['model']
        format_type = options['format']
        dry_run = options['dry_run']
        
        self.stdout.write(f"Importing {model_name} data from {file_path} (format: {format_type}, dry_run: {dry_run})...")
        
        try:
            if format_type == 'json':
                data = self._load_json(file_path)
            else:
                data = self._load_csv(file_path)
            
            imported_count = 0
            error_count = 0
            
            for item in data:
                try:
                    if not dry_run:
                        self._import_item(model_name, item)
                    imported_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Imported: {item}"))
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f"Error importing {item}: {e}"))
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Import completed. Imported: {imported_count}, Errors: {error_count}'
                    )
                )
            else:
                self.stdout.write(
                    f'Dry run completed. Would import: {imported_count}, Would error: {error_count}'
                )
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Import failed: {e}"))
    
    def _load_json(self, file_path):
        """Load data from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_csv(self, file_path):
        """Load data from CSV file."""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    def _import_item(self, model_name, item):
        """Import a single item."""
        if model_name == 'job':
            from apps.jobs.models import Job, Category
            from apps.accounts.models import User
            
            # Get related objects
            category = Category.objects.get(id=item['category_id'])
            employer = User.objects.get(id=item['employer_id'])
            
            Job.objects.create(
                title=item['title'],
                description=item['description'],
                requirements=item.get('requirements', ''),
                category=category,
                employer=employer,
                location=item['location'],
                job_type=item.get('job_type', 'full-time'),
                salary_min=item.get('salary_min'),
                salary_max=item.get('salary_max'),
                status=item.get('status', 'draft'),
            )
        elif model_name == 'user':
            from apps.accounts.models import User
            User.objects.create_user(
                username=item['username'],
                email=item['email'],
                password=item.get('password', 'defaultpassword123'),
                first_name=item.get('first_name', ''),
                last_name=item.get('last_name', ''),
                role=item.get('role', 'user'),
            )
        elif model_name == 'category':
            from apps.jobs.models import Category
            Category.objects.create(
                name=item['name'],
                description=item.get('description', ''),
                parent_id=item.get('parent_id'),
            )
        # Add more models as needed
