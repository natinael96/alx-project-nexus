"""
Management command to create admin users programmatically.
Useful for Docker deployments and automated setups.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an admin user (superuser with admin role)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the admin user',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the admin user',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the admin user (if not provided, will prompt)',
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Run non-interactively (requires --username, --email, --password)',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing user if username or email already exists',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        no_input = options.get('no_input', False)
        update = options.get('update', False)

        # Interactive mode
        if not no_input:
            if not username:
                username = input('Username: ')
            if not email:
                email = input('Email address: ')
            if not password:
                password = getpass.getpass('Password: ')
                password_confirm = getpass.getpass('Password (again): ')
                if password != password_confirm:
                    raise CommandError('Passwords do not match.')
        else:
            # Non-interactive mode - all fields required
            if not username:
                raise CommandError('--username is required in non-interactive mode.')
            if not email:
                raise CommandError('--email is required in non-interactive mode.')
            if not password:
                raise CommandError('--password is required in non-interactive mode.')

        # Validate inputs
        if not username or not username.strip():
            raise CommandError('Username cannot be empty.')
        if not email or not email.strip():
            raise CommandError('Email cannot be empty.')
        if not password or len(password) < 8:
            raise CommandError('Password must be at least 8 characters long.')

        username = username.strip()
        email = email.strip().lower()

        try:
            with transaction.atomic():
                # Check if user already exists
                user = None
                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    if not update:
                        raise CommandError(
                            f'User with username "{username}" already exists. '
                            'Use --update to update existing user.'
                        )
                    self.stdout.write(
                        self.style.WARNING(f'Updating existing user: {username}')
                    )
                elif User.objects.filter(email=email).exists():
                    user = User.objects.get(email=email)
                    if not update:
                        raise CommandError(
                            f'User with email "{email}" already exists. '
                            'Use --update to update existing user.'
                        )
                    self.stdout.write(
                        self.style.WARNING(f'Updating existing user: {email}')
                    )

                if user:
                    # Update existing user
                    user.email = email
                    user.set_password(password)
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.role = 'admin'
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully updated admin user "{username}"'
                        )
                    )
                else:
                    # Create new user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_staff=True,
                        is_superuser=True,
                        is_active=True,
                        role='admin'
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created admin user "{username}"'
                        )
                    )

                # Display user info
                self.stdout.write(f'  Username: {user.username}')
                self.stdout.write(f'  Email: {user.email}')
                self.stdout.write(f'  Role: {user.role}')
                self.stdout.write(f'  Is Superuser: {user.is_superuser}')
                self.stdout.write(f'  Is Staff: {user.is_staff}')

        except Exception as e:
            raise CommandError(f'Error creating admin user: {str(e)}')
