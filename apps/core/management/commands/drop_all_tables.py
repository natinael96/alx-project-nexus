"""
Management command to drop all tables and recreate schema.
Use this when you need to completely reset the database schema.
"""
from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = 'Drop all tables and recreate schema (WARNING: Destructive operation)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to drop all tables (required for safety)',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR(
                    '\n⚠️  WARNING: This will DROP ALL TABLES and DELETE ALL DATA!\n'
                    'This action cannot be undone.\n'
                    'Use --confirm flag to proceed.\n'
                )
            )
            return

        self.stdout.write(self.style.WARNING('Starting to drop all tables...'))

        try:
            with connection.cursor() as cursor:
                # Get all table names
                cursor.execute("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    AND tablename NOT LIKE 'pg_%'
                    ORDER BY tablename;
                """)
                tables = [row[0] for row in cursor.fetchall()]

                if not tables:
                    self.stdout.write(self.style.WARNING('No tables found to drop.'))
                    return

                self.stdout.write(f'\nFound {len(tables)} tables to drop:')
                for table in tables:
                    self.stdout.write(f'  - {table}')

                # Drop all tables using CASCADE to handle foreign keys
                dropped_count = 0
                for table in tables:
                    try:
                        cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
                        dropped_count += 1
                        if options.get('verbosity', 1) >= 2:
                            self.stdout.write(f'  ✓ Dropped {table}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  ✗ Failed to drop {table}: {str(e)}')
                        )

                # Also drop sequences
                cursor.execute("""
                    SELECT sequence_name 
                    FROM information_schema.sequences 
                    WHERE sequence_schema = 'public';
                """)
                sequences = [row[0] for row in cursor.fetchall()]
                
                for sequence in sequences:
                    try:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS "{sequence}" CASCADE;')
                        if options.get('verbosity', 1) >= 2:
                            self.stdout.write(f'  ✓ Dropped sequence {sequence}')
                    except Exception as e:
                        if options.get('verbosity', 1) >= 2:
                            self.stdout.write(
                                self.style.WARNING(f'  Could not drop sequence {sequence}: {str(e)}')
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✓ Successfully dropped {dropped_count} tables!'
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        '\nNext steps:'
                        '\n  1. Delete problematic migrations (the ones trying to alter IDs)'
                        '\n  2. Run: python manage.py makemigrations'
                        '\n  3. Run: python manage.py migrate'
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error dropping tables: {str(e)}'))
            if options.get('verbosity', 1) >= 2:
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise
