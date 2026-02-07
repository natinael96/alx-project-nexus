"""
Management command to process job expiration and auto-close.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.jobs.models import Job
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process job expiration and auto-close expired jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually closing jobs',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(f"Processing job expiration (dry_run={dry_run})...")
        
        now = timezone.now()
        expired_jobs = Job.objects.filter(
            status='active',
            expires_at__lte=now
        )
        
        closed_count = 0
        renewed_count = 0
        
        for job in expired_jobs:
            try:
                if job.auto_renew:
                    # Renew the job
                    renewal_days = 30  # Default renewal period
                    job.expires_at = now + timezone.timedelta(days=renewal_days)
                    job.renewal_count += 1
                    job.save(update_fields=['expires_at', 'renewal_count'])
                    renewed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Renewed job: {job.title} (ID: {job.id})")
                    )
                else:
                    # Close the job
                    if not dry_run:
                        job.status = 'closed'
                        job.save(update_fields=['status'])
                    closed_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"{'Would close' if dry_run else 'Closed'} job: {job.title} (ID: {job.id})")
                    )
            except Exception as e:
                logger.error(f"Error processing job {job.id}: {e}")
                self.stdout.write(
                    self.style.ERROR(f"Error processing job {job.id}: {e}")
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Processed {expired_jobs.count()} expired jobs. '
                    f'Closed: {closed_count}, Renewed: {renewal_count}'
                )
            )
        else:
            self.stdout.write(
                f'Would process {expired_jobs.count()} expired jobs. '
                f'Would close: {closed_count}, Would renew: {renewal_count}'
            )
