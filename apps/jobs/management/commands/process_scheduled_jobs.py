"""
Management command to publish scheduled jobs.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.jobs.models import Job
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Publish scheduled jobs that are ready to be published'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually publishing jobs',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(f"Processing scheduled jobs (dry_run={dry_run})...")
        
        now = timezone.now()
        scheduled_jobs = Job.objects.filter(
            status='draft',
            scheduled_publish_date__lte=now,
            approval_status='approved'  # Only publish approved jobs
        )
        
        published_count = 0
        
        for job in scheduled_jobs:
            try:
                if not dry_run:
                    job.status = 'active'
                    job.scheduled_publish_date = None  # Clear scheduled date
                    job.save(update_fields=['status', 'scheduled_publish_date'])
                published_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{'Would publish' if dry_run else 'Published'} job: {job.title} (ID: {job.id})"
                    )
                )
            except Exception as e:
                logger.error(f"Error publishing job {job.id}: {e}")
                self.stdout.write(
                    self.style.ERROR(f"Error publishing job {job.id}: {e}")
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Published {published_count} scheduled jobs')
            )
        else:
            self.stdout.write(f'Would publish {published_count} scheduled jobs')
