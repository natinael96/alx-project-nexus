"""
Management command to process search alerts and send notifications.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models_search import SearchAlert
from apps.jobs.search_service import AdvancedSearchService
from apps.core.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process search alerts and send notifications for new matching jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--frequency',
            type=str,
            choices=['daily', 'weekly', 'immediate'],
            help='Process alerts with specific frequency (default: all)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending',
        )

    def handle(self, *args, **options):
        frequency = options.get('frequency')
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(f"Processing search alerts (frequency={frequency or 'all'}, dry_run={dry_run})...")
        
        # Get active alerts
        alerts = SearchAlert.objects.filter(is_active=True)
        if frequency:
            alerts = alerts.filter(frequency=frequency)
        
        processed_count = 0
        notified_count = 0
        
        for alert in alerts:
            try:
                # Check if it's time to process this alert
                if not self._should_process_alert(alert, frequency):
                    continue
                
                # Perform search
                queryset, total_count = AdvancedSearchService.search_jobs(
                    query=alert.search_query,
                    filters=alert.filters,
                    user=alert.user
                )
                
                # Find new jobs (jobs created after last notification)
                if alert.last_notified_at:
                    new_jobs = queryset.filter(created_at__gt=alert.last_notified_at)
                else:
                    # First time - get recent jobs (last 7 days)
                    cutoff = timezone.now() - timedelta(days=7)
                    new_jobs = queryset.filter(created_at__gte=cutoff)
                
                # Limit to top 10 new jobs
                new_jobs = new_jobs[:10]
                
                if new_jobs.exists():
                    if dry_run:
                        self.stdout.write(
                            f"Would notify {alert.user.username} about {new_jobs.count()} new jobs for alert '{alert.name}'"
                        )
                    else:
                        # Send notification email
                        self._send_alert_notification(alert, new_jobs, total_count)
                        alert.last_notified_at = timezone.now()
                        if new_jobs.first():
                            alert.last_job_id = new_jobs.first().id
                        alert.save(update_fields=['last_notified_at', 'last_job_id'])
                        notified_count += 1
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing alert {alert.id}: {e}")
                self.stdout.write(self.style.ERROR(f"Error processing alert {alert.id}: {e}"))
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Processed {processed_count} alerts, sent {notified_count} notifications'
                )
            )
        else:
            self.stdout.write(f'Would process {processed_count} alerts')

    def _should_process_alert(self, alert, frequency_filter):
        """Check if alert should be processed based on frequency and last notification."""
        if not alert.last_notified_at:
            return True  # Never notified, process it
        
        now = timezone.now()
        last_notified = alert.last_notified_at
        
        if alert.frequency == 'immediate':
            # Check every time (or could be triggered by job creation)
            return True
        elif alert.frequency == 'daily':
            # Check if 24 hours have passed
            return (now - last_notified).total_seconds() >= 86400
        elif alert.frequency == 'weekly':
            # Check if 7 days have passed
            return (now - last_notified).total_seconds() >= 604800
        
        return False
    
    def _send_alert_notification(self, alert, new_jobs, total_count):
        """Send email notification for search alert."""
        try:
            # This would use a new email template for search alerts
            # For now, we'll log it
            logger.info(
                f"Sending search alert notification to {alert.user.email} "
                f"for alert '{alert.name}' with {new_jobs.count()} new jobs"
            )
            # TODO: Implement email template for search alerts
            # EmailService.send_search_alert_notification(alert, new_jobs, total_count)
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
