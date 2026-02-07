"""
Management command to seed the database with test data.
Creates users, categories, jobs, applications, and related data for testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from decimal import Decimal
import random

User = get_user_model()

# Import models
from apps.jobs.models import (
    Category, Job, Application
)
from apps.accounts.models_profile import (
    Skill, Education, WorkHistory, Portfolio,
    SocialLink, UserPreferences, SavedJob
)


class Command(BaseCommand):
    help = 'Seed the database with test data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of regular users to create (default: 20)',
        )
        parser.add_argument(
            '--employers',
            type=int,
            default=10,
            help='Number of employer users to create (default: 10)',
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=50,
            help='Number of jobs to create (default: 50)',
        )
        parser.add_argument(
            '--applications',
            type=int,
            default=30,
            help='Number of applications to create (default: 30)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding (WARNING: deletes all data)',
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_employers = options['employers']
        num_jobs = options['jobs']
        num_applications = options['applications']
        clear = options['clear']
        verbosity = options.get('verbosity', 1)

        if clear:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            if verbosity >= 2:
                self.stdout.write('  - Deleting applications...')
            self._clear_data(verbosity)

        self.stdout.write(self.style.SUCCESS('Starting to seed data...'))
        if verbosity >= 2:
            self.stdout.write(f'  - Users: {num_users}')
            self.stdout.write(f'  - Employers: {num_employers}')
            self.stdout.write(f'  - Jobs: {num_jobs}')
            self.stdout.write(f'  - Applications: {num_applications}')

        try:
            with transaction.atomic():
                # Create categories
                if verbosity >= 2:
                    self.stdout.write('\n[1/7] Creating categories...')
                categories = self._create_categories(verbosity)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(categories)} categories'))

                # Create admin user
                if verbosity >= 2:
                    self.stdout.write('\n[2/7] Creating admin user...')
                admin = self._create_admin_user(verbosity)
                self.stdout.write(self.style.SUCCESS(f'✓ Created admin user: {admin.username}'))

                # Create employer users
                if verbosity >= 2:
                    self.stdout.write(f'\n[3/7] Creating {num_employers} employer users...')
                employers = self._create_employers(num_employers, verbosity)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(employers)} employer users'))

                # Create regular users
                if verbosity >= 2:
                    self.stdout.write(f'\n[4/7] Creating {num_users} regular users...')
                users = self._create_users(num_users, verbosity)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(users)} regular users'))

                # Create jobs
                if verbosity >= 2:
                    self.stdout.write(f'\n[5/7] Creating {num_jobs} jobs...')
                jobs = self._create_jobs(num_jobs, employers, categories, verbosity)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(jobs)} jobs'))

                # Create applications
                if verbosity >= 2:
                    self.stdout.write(f'\n[6/7] Creating {num_applications} applications...')
                applications = self._create_applications(num_applications, users, jobs, verbosity)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(applications)} applications'))

                # Create user profiles
                if verbosity >= 2:
                    self.stdout.write(f'\n[7/7] Creating user profiles for {len(users) + len(employers)} users...')
                self._create_user_profiles(users + employers, verbosity)
                self.stdout.write(self.style.SUCCESS('✓ Created user profiles'))

                # Create saved jobs
                if verbosity >= 2:
                    self.stdout.write('\nCreating saved jobs...')
                self._create_saved_jobs(users, jobs, verbosity)
                self.stdout.write(self.style.SUCCESS('✓ Created saved jobs'))

            self.stdout.write(self.style.SUCCESS('\n✓ Data seeding completed successfully!'))
            self.stdout.write(f'\nSummary:')
            self.stdout.write(f'  - Admin users: 1')
            self.stdout.write(f'  - Employer users: {len(employers)}')
            self.stdout.write(f'  - Regular users: {len(users)}')
            self.stdout.write(f'  - Categories: {len(categories)}')
            self.stdout.write(f'  - Jobs: {len(jobs)}')
            self.stdout.write(f'  - Applications: {len(applications)}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error seeding data: {str(e)}'))
            if verbosity >= 2:
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise

    def _clear_data(self, verbosity=1):
        """Clear existing data."""
        if verbosity >= 2:
            self.stdout.write('  - Deleting applications...')
        app_count = Application.objects.count()
        Application.objects.all().delete()
        if verbosity >= 2:
            self.stdout.write(f'    Deleted {app_count} applications')
        
        if verbosity >= 2:
            self.stdout.write('  - Deleting jobs...')
        job_count = Job.objects.count()
        Job.objects.all().delete()
        if verbosity >= 2:
            self.stdout.write(f'    Deleted {job_count} jobs')
        
        if verbosity >= 2:
            self.stdout.write('  - Deleting categories...')
        cat_count = Category.objects.count()
        Category.objects.all().delete()
        if verbosity >= 2:
            self.stdout.write(f'    Deleted {cat_count} categories')
        
        if verbosity >= 2:
            self.stdout.write('  - Deleting users (except superusers)...')
        user_count = User.objects.filter(is_superuser=False).count()
        User.objects.filter(is_superuser=False).delete()
        if verbosity >= 2:
            self.stdout.write(f'    Deleted {user_count} users')
        
        self.stdout.write(self.style.WARNING('Existing data cleared.'))

    def _create_categories(self, verbosity=1):
        """Create job categories."""
        categories_data = [
            {'name': 'Technology', 'description': 'Software development, IT, and tech jobs'},
            {'name': 'Healthcare', 'description': 'Medical, nursing, and healthcare positions'},
            {'name': 'Finance', 'description': 'Banking, accounting, and financial services'},
            {'name': 'Education', 'description': 'Teaching, training, and educational roles'},
            {'name': 'Marketing', 'description': 'Digital marketing, advertising, and PR'},
            {'name': 'Sales', 'description': 'Sales and business development roles'},
            {'name': 'Design', 'description': 'Graphic design, UI/UX, and creative roles'},
            {'name': 'Engineering', 'description': 'Mechanical, electrical, and civil engineering'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if verbosity >= 3:
                self.stdout.write(f'    {"Created" if created else "Found"} category: {category.name}')
            categories.append(category)

        # Create subcategories
        tech = Category.objects.get(name='Technology')
        subcategories = [
            {'name': 'Software Development', 'parent': tech},
            {'name': 'Data Science', 'parent': tech},
            {'name': 'DevOps', 'parent': tech},
            {'name': 'Cybersecurity', 'parent': tech},
        ]

        for subcat_data in subcategories:
            subcat, created = Category.objects.get_or_create(
                name=subcat_data['name'],
                defaults={'parent': subcat_data['parent']}
            )
            if verbosity >= 3:
                self.stdout.write(f'    {"Created" if created else "Found"} subcategory: {subcat.name}')

        return categories

    def _create_admin_user(self, verbosity=1):
        """Create an admin user."""
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@jobboard.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            if verbosity >= 2:
                self.stdout.write(f'    Created admin user: {admin.username} (ID: {admin.id})')
        else:
            if verbosity >= 2:
                self.stdout.write(f'    Admin user already exists: {admin.username} (ID: {admin.id})')
        return admin

    def _create_employers(self, count, verbosity=1):
        """Create employer users."""
        employers = []
        companies = [
            'TechCorp', 'InnovateLabs', 'GlobalSolutions', 'StartupHub',
            'DigitalWorks', 'CloudSystems', 'DataDriven', 'FutureTech',
            'SmartSolutions', 'NextGen', 'CodeMasters', 'DevStudio'
        ]

        for i in range(count):
            company = companies[i % len(companies)]
            base_username = f'employer_{company.lower()}_{i+1}'
            username = base_username
            email = f'{username}@example.com'
            
            # Ensure unique username and email
            counter = 1
            while User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                username = f'{base_username}_{counter}'
                email = f'{username}@example.com'
                counter += 1
                if counter > 1000:  # Safety limit
                    raise ValueError(f"Could not generate unique username for employer {company}")

            try:
                employer = User.objects.create(
                    username=username,
                    email=email,
                    first_name=company,
                    last_name='Recruiter',
                    role='employer',
                    is_active=True,
                )
                employer.set_password('employer123')
                employer.save()
                employers.append(employer)
                if verbosity >= 2:
                    self.stdout.write(f'    Created employer: {employer.username} (ID: {employer.id}, Email: {employer.email})')
            except Exception as e:
                if verbosity >= 1:
                    self.stdout.write(self.style.ERROR(f'    Failed to create employer {username}: {str(e)}'))
                raise

        return employers

    def _create_users(self, count, verbosity=1):
        """Create regular users."""
        users = []
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']

        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            base_username = f'user_{first_name.lower()}_{last_name.lower()}_{i+1}'
            username = base_username
            email = f'{username}@example.com'
            
            # Ensure unique username and email
            counter = 1
            while User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                username = f'{base_username}_{counter}'
                email = f'{username}@example.com'
                counter += 1
                if counter > 1000:  # Safety limit
                    raise ValueError(f"Could not generate unique username for user {first_name} {last_name}")

            try:
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role='user',
                    is_active=True,
                )
                user.set_password('user123')
                user.save()
                users.append(user)
                if verbosity >= 2:
                    self.stdout.write(f'    Created user: {user.username} (ID: {user.id}, Email: {user.email})')
            except Exception as e:
                if verbosity >= 1:
                    self.stdout.write(self.style.ERROR(f'    Failed to create user {username}: {str(e)}'))
                raise

        return users

    def _create_jobs(self, count, employers, categories, verbosity=1):
        """Create jobs."""
        jobs = []
        job_titles = [
            'Senior Software Engineer', 'Frontend Developer', 'Backend Developer',
            'Full Stack Developer', 'DevOps Engineer', 'Data Scientist',
            'Product Manager', 'UX Designer', 'Marketing Manager', 'Sales Representative',
            'Project Manager', 'Business Analyst', 'QA Engineer', 'Mobile Developer',
            'Cloud Architect', 'Security Engineer', 'Content Writer', 'Graphic Designer'
        ]

        locations = [
            'New York, NY', 'San Francisco, CA', 'Austin, TX', 'Seattle, WA',
            'Boston, MA', 'Chicago, IL', 'Los Angeles, CA', 'Remote'
        ]

        job_types = ['full-time', 'part-time', 'contract', 'internship', 'freelance']
        statuses = ['draft', 'active', 'active', 'active', 'closed']  # More active jobs
        approval_statuses = ['pending', 'approved', 'approved', 'approved', 'rejected']

        for i in range(count):
            employer = random.choice(employers)
            category = random.choice(categories)
            title = random.choice(job_titles)
            location = random.choice(locations)
            job_type = random.choice(job_types)
            status = random.choice(statuses)
            approval_status = random.choice(approval_statuses) if status == 'active' else 'pending'

            # Salary range (convert to Decimal for DecimalField)
            salary_min = Decimal(random.randint(50000, 100000))
            salary_max = Decimal(salary_min + random.randint(20000, 50000))

            # Dates
            created_at = timezone.now() - timedelta(days=random.randint(0, 90))
            expires_at = timezone.now() + timedelta(days=random.randint(7, 60)) if status == 'active' else None
            application_deadline = timezone.now() + timedelta(days=random.randint(7, 30)) if status == 'active' else None

            # Create job first (created_at will be auto-set, then we'll update it)
            job = Job.objects.create(
                title=title,
                description=f'We are looking for an experienced {title} to join our team. '
                           f'This is a great opportunity to work on exciting projects and grow your career.',
                requirements=f'Requirements:\n- 3+ years of experience\n- Strong problem-solving skills\n'
                           f'- Excellent communication skills\n- Bachelor\'s degree preferred',
                category=category,
                employer=employer,
                location=location,
                job_type=job_type,
                salary_min=salary_min,
                salary_max=salary_max,
                status=status,
                approval_status=approval_status,
                is_featured=random.choice([True, False, False, False]),  # 25% featured
                expires_at=expires_at,
                application_deadline=application_deadline.date() if application_deadline else None,
            )
            
            # Update created_at manually (bypass auto_now_add)
            Job.objects.filter(pk=job.pk).update(created_at=created_at)
            job.refresh_from_db()

            if approval_status == 'approved' and status == 'active':
                job.approved_by = employer
                job.approved_at = created_at
                job.save()

            jobs.append(job)
            if verbosity >= 3:
                self.stdout.write(f'    Created job: {job.title} (ID: {job.id}, Status: {job.status})')

        return jobs

    def _create_applications(self, count, users, jobs, verbosity=1):
        """Create job applications."""
        applications = []
        active_jobs = [job for job in jobs if job.status == 'active' and job.approval_status == 'approved']
        
        if not active_jobs:
            self.stdout.write(self.style.WARNING('No active approved jobs found. Skipping applications.'))
            return []

        statuses = ['pending', 'pending', 'pending', 'reviewed', 'accepted', 'rejected']
        
        if verbosity >= 2:
            self.stdout.write(f'    Found {len(active_jobs)} active approved jobs')

        created_count = 0
        skipped_count = 0
        for i in range(min(count, len(users) * len(active_jobs))):
            user = random.choice(users)
            job = random.choice(active_jobs)
            
            # Check if user already applied
            if Application.objects.filter(job=job, applicant=user).exists():
                skipped_count += 1
                if verbosity >= 3:
                    self.stdout.write(f'    Skipped: {user.username} already applied to {job.title}')
                continue

            status = random.choice(statuses)
            applied_at = timezone.now() - timedelta(days=random.randint(0, 30))

            # Create a dummy resume file for seeding (minimal valid PDF)
            from django.core.files.base import ContentFile
            # Generate a simple valid PDF with proper structure
            user_name = user.get_full_name() or user.username
            text_content = f'Resume for {user_name}'.encode('utf-8')
            stream_content = b'BT\n/F1 12 Tf\n100 700 Td\n(' + text_content + b') Tj\nET'
            stream_length = len(stream_content)
            
            # Build PDF with correct length
            pdf_parts = [
                b'%PDF-1.4',
                b'1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj',
                b'2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj',
                b'3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n/Resources <<\n/Font <<\n/F1 <<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\n>>\n>>\n>>\nendobj',
                f'4 0 obj\n<<\n/Length {stream_length}\n>>\nstream\n'.encode('utf-8') + stream_content + b'\nendstream\nendobj',
                b'xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000306 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n398\n%%EOF'
            ]
            pdf_content = b'\n'.join(pdf_parts)
            resume_file = ContentFile(pdf_content, name=f'{user.username}_resume.pdf')

            try:
                # Create application first (applied_at will be auto-set, then we'll update it)
                application = Application.objects.create(
                    job=job,
                    applicant=user,
                    cover_letter=f'Dear Hiring Manager,\n\nI am writing to express my interest in the {job.title} position. '
                               f'I believe my skills and experience make me a strong candidate for this role.\n\n'
                               f'Best regards,\n{user.get_full_name()}',
                    resume=resume_file,
                    status=status,
                )
                
                # Update applied_at manually (bypass auto_now_add)
                Application.objects.filter(pk=application.pk).update(applied_at=applied_at)
                application.refresh_from_db()

                if status != 'pending':
                    application.reviewed_at = applied_at + timedelta(days=random.randint(1, 7))
                    application.save()

                applications.append(application)
                created_count += 1
                if verbosity >= 3:
                    self.stdout.write(f'    Created application: {user.username} -> {job.title} (ID: {application.id}, Status: {status})')
            except Exception as e:
                if verbosity >= 2:
                    self.stdout.write(self.style.ERROR(f'    Failed to create application for {user.username} -> {job.title}: {str(e)}'))
                raise

        if verbosity >= 2:
            self.stdout.write(f'    Created {created_count} applications, skipped {skipped_count} duplicates')

        return applications

    def _create_user_profiles(self, users, verbosity=1):
        """Create user profiles with skills, education, work history, etc."""
        skills_list = [
            'Python', 'JavaScript', 'Java', 'React', 'Django', 'Node.js',
            'PostgreSQL', 'MongoDB', 'AWS', 'Docker', 'Kubernetes', 'Git',
            'HTML', 'CSS', 'TypeScript', 'Vue.js', 'Angular', 'Flask',
            'Machine Learning', 'Data Analysis', 'Project Management', 'Agile'
        ]

        degrees = [
            'Bachelor of Science', 'Bachelor of Arts', 'Master of Science',
            'Master of Business Administration', 'Bachelor of Engineering'
        ]

        fields = [
            'Computer Science', 'Software Engineering', 'Information Technology',
            'Business Administration', 'Marketing', 'Finance', 'Engineering'
        ]

        companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Netflix',
            'Tesla', 'IBM', 'Oracle', 'Salesforce', 'Adobe', 'Intel'
        ]

        positions = [
            'Software Engineer', 'Senior Developer', 'Tech Lead', 'Product Manager',
            'Data Analyst', 'Marketing Specialist', 'Business Analyst', 'Designer'
        ]

        for idx, user in enumerate(users, 1):
            if verbosity >= 2:
                self.stdout.write(f'    Creating profile for user {idx}/{len(users)}: {user.username}')
            
            # Create preferences
            prefs, created = UserPreferences.objects.get_or_create(user=user)
            if verbosity >= 3:
                self.stdout.write(f'      {"Created" if created else "Found"} preferences')

            # Create skills (2-5 per user)
            num_skills = random.randint(2, 5)
            user_skills = random.sample(skills_list, min(num_skills, len(skills_list)))
            for skill_name in user_skills:
                skill, created = Skill.objects.get_or_create(
                    user=user,
                    name=skill_name,
                    defaults={
                        'level': random.choice(['beginner', 'intermediate', 'advanced', 'expert']),
                        'years_of_experience': random.randint(1, 10),
                    }
                )
                if verbosity >= 3:
                    self.stdout.write(f'      {"Created" if created else "Found"} skill: {skill_name}')

            # Create education (1-2 per user)
            num_education = random.randint(1, 2)
            for i in range(num_education):
                start_year = random.randint(2010, 2020)
                end_year = start_year + random.randint(3, 5) if random.choice([True, False]) else None
                edu, created = Education.objects.get_or_create(
                    user=user,
                    institution=f'University {random.randint(1, 10)}',
                    degree=random.choice(degrees),
                    field_of_study=random.choice(fields),
                    defaults={
                        'start_date': datetime(start_year, 9, 1).date(),
                        'end_date': datetime(end_year, 6, 1).date() if end_year else None,
                        'is_current': end_year is None,
                    }
                )
                if verbosity >= 3:
                    self.stdout.write(f'      {"Created" if created else "Found"} education: {edu.degree}')

            # Create work history (1-3 per user)
            num_work = random.randint(1, 3)
            for i in range(num_work):
                start_year = random.randint(2015, 2022)
                end_year = start_year + random.randint(1, 4) if i < num_work - 1 else None
                work, created = WorkHistory.objects.get_or_create(
                    user=user,
                    company=random.choice(companies),
                    position=random.choice(positions),
                    defaults={
                        'start_date': datetime(start_year, 1, 1).date(),
                        'end_date': datetime(end_year, 12, 31).date() if end_year else None,
                        'is_current': end_year is None,
                        'description': f'Responsible for various tasks and projects.',
                        'location': random.choice(['New York, NY', 'San Francisco, CA', 'Remote']),
                    }
                )
                if verbosity >= 3:
                    self.stdout.write(f'      {"Created" if created else "Found"} work history: {work.position} at {work.company}')

            # Create social links (1-2 per user)
            platforms = ['linkedin', 'github', 'twitter']
            num_links = random.randint(1, 2)
            for platform in random.sample(platforms, min(num_links, len(platforms))):
                link, created = SocialLink.objects.get_or_create(
                    user=user,
                    platform=platform,
                    defaults={
                        'url': f'https://{platform}.com/{user.username}',
                        'is_public': True,
                    }
                )
                if verbosity >= 3:
                    self.stdout.write(f'      {"Created" if created else "Found"} social link: {platform}')

    def _create_saved_jobs(self, users, jobs, verbosity=1):
        """Create saved jobs/bookmarks."""
        active_jobs = [job for job in jobs if job.status == 'active']
        
        if verbosity >= 2:
            self.stdout.write(f'    Found {len(active_jobs)} active jobs to save')
        
        saved_count = 0
        for user in users[:len(users)//2]:  # Only half of users save jobs
            num_saved = random.randint(1, 5)
            saved_jobs = random.sample(active_jobs, min(num_saved, len(active_jobs)))
            
            for job in saved_jobs:
                saved_job, created = SavedJob.objects.get_or_create(
                    user=user,
                    job=job,
                    defaults={
                        'notes': f'Interested in this {job.job_type} position.',
                    }
                )
                if created:
                    saved_count += 1
                    if verbosity >= 3:
                        self.stdout.write(f'    User {user.username} saved job: {job.title}')
        
        if verbosity >= 2:
            self.stdout.write(f'    Created {saved_count} saved jobs')