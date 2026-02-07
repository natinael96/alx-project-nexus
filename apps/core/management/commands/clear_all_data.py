"""
Management command to clear all data from all tables while preserving table structure.
"""
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.apps import apps
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Clear all data from all tables while preserving table structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data (required for safety)',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR(
                    '\n⚠️  WARNING: This will delete ALL data from ALL tables!\n'
                    'This action cannot be undone.\n'
                    'Use --confirm flag to proceed.\n'
                )
            )
            return

        self.stdout.write(self.style.WARNING('Starting to clear all data...'))

        try:
            with transaction.atomic():
                # Disable foreign key checks temporarily (PostgreSQL specific)
                with connection.cursor() as cursor:
                    # Get all table names
                    cursor.execute("""
                        SELECT tablename 
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                        AND tablename NOT LIKE 'pg_%'
                        AND tablename NOT LIKE 'django_%'
                        ORDER BY tablename;
                    """)
                    tables = [row[0] for row in cursor.fetchall()]

                    if not tables:
                        self.stdout.write(self.style.WARNING('No tables found to clear.'))
                        return

                    self.stdout.write(f'\nFound {len(tables)} tables to clear:')
                    for table in tables:
                        self.stdout.write(f'  - {table}')

                    # Clear all tables using TRUNCATE CASCADE
                    # This will handle foreign key constraints automatically
                    cleared_count = 0
                    for table in tables:
                        try:
                            cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE;')
                            cleared_count += 1
                            if options.get('verbosity', 1) >= 2:
                                self.stdout.write(f'  ✓ Cleared {table}')
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'  ✗ Failed to clear {table}: {str(e)}')
                            )

                # Clear Django content types cache
                ContentType.objects.clear_cache()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✓ Successfully cleared data from {cleared_count} tables!'
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        '\nNote: Table structures are preserved. '
                        'You can now run migrations or seed data.'
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error clearing data: {str(e)}'))
            if options.get('verbosity', 1) >= 2:
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise
