"""
Pytest configuration and fixtures for testing.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.jobs.models import Category, Job, Application

User = get_user_model()


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a regular user for testing."""
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        role='user'
    )


@pytest.fixture
def employer(db):
    """Create an employer user for testing."""
    return User.objects.create_user(
        username='employer',
        email='employer@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Employer',
        role='employer'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User',
        role='admin'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def employer_client(api_client, employer):
    """Create an authenticated employer API client."""
    api_client.force_authenticate(user=employer)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create an authenticated admin API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def category(db):
    """Create a category for testing."""
    return Category.objects.create(
        name='Software Development',
        description='Software development jobs',
        slug='software-development'
    )


@pytest.fixture
def job(db, employer, category):
    """Create a job for testing."""
    return Job.objects.create(
        title='Senior Python Developer',
        description='We are looking for an experienced Python developer.',
        requirements='5+ years of Python experience',
        category=category,
        employer=employer,
        location='New York, NY',
        job_type='full-time',
        salary_min=80000,
        salary_max=120000,
        status='active'
    )


@pytest.fixture
def application(db, user, job):
    """Create an application for testing."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    resume = SimpleUploadedFile(
        "resume.pdf",
        b"file_content",
        content_type="application/pdf"
    )
    return Application.objects.create(
        job=job,
        applicant=user,
        cover_letter='I am interested in this position.',
        resume=resume,
        status='pending'
    )
