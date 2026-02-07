"""
Management command to clean up old and orphaned files.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import Application
from apps.accounts.models import User
from apps.core.file_management import FileCleanup
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up old and orphaned files from storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete files older than this many days (default: 90)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--applications',
            action='store_true',
            help='Clean up application files',
        )
        parser.add_argument(
            '--profiles',
            action='store_true',
            help='Clean up profile picture files',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cleanup_applications = options['applications']
        cleanup_profiles = options['profiles']
        
        if not cleanup_applications and not cleanup_profiles:
            # Clean up both if neither is specified
            cleanup_applications = True
            cleanup_profiles = True
        
        self.stdout.write(f"Starting file cleanup (days={days}, dry_run={dry_run})...")
        
        if cleanup_applications:
            self.stdout.write("Cleaning up application files...")
            self._cleanup_application_files(days, dry_run)
        
        if cleanup_profiles:
            self.stdout.write("Cleaning up profile picture files...")
            self._cleanup_profile_files(days, dry_run)
        
        self.stdout.write(self.style.SUCCESS('File cleanup completed!'))

    def _cleanup_application_files(self, days, dry_run):
        """Clean up old application files."""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find applications with files older than cutoff
        old_applications = Application.objects.filter(
            applied_at__lt=cutoff_date
        ).exclude(resume='')
        
        count = 0
        for application in old_applications:
            if application.resume:
                if dry_run:
                    self.stdout.write(
                        f"Would delete: {application.resume} (Application ID: {application.id})"
                    )
                else:
                    from apps.core.file_management import FileCleanup
                    if FileCleanup.delete_file_safely(str(application.resume)):
                        count += 1
        
        if not dry_run:
            self.stdout.write(f"Deleted {count} application files")
        else:
            self.stdout.write(f"Would delete {old_applications.count()} application files")

    def _cleanup_profile_files(self, days, dry_run):
        """Clean up old profile picture files."""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find users with profile pictures older than cutoff
        old_users = User.objects.filter(
            date_joined__lt=cutoff_date
        ).exclude(profile_picture='')
        
        count = 0
        for user in old_users:
            if user.profile_picture:
                if dry_run:
                    self.stdout.write(
                        f"Would delete: {user.profile_picture} (User ID: {user.id})"
                    )
                else:
                    from apps.core.file_management import FileCleanup
                    if FileCleanup.delete_file_safely(str(user.profile_picture)):
                        count += 1
        
        if not dry_run:
            self.stdout.write(f"Deleted {count} profile picture files")
        else:
            self.stdout.write(f"Would delete {old_users.count()} profile picture files")
