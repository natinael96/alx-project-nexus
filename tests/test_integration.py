"""
Integration tests for complete workflows.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from apps.accounts.models import User
from apps.jobs.models import Category, Job, Application


class TestAuthenticationFlow:
    """Integration tests for authentication workflow."""
    
    def test_complete_registration_login_flow(self, api_client):
        """Test complete user registration and login flow."""
        # Register
        register_url = reverse('accounts:register')
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        register_response = api_client.post(register_url, register_data, format='json')
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Login
        login_url = reverse('accounts:login')
        login_data = {
            'username': 'newuser',
            'password': 'SecurePass123!'
        }
        login_response = api_client.post(login_url, login_data, format='json')
        assert login_response.status_code == status.HTTP_200_OK
        assert 'access' in login_response.data
        
        # Use token to access protected endpoint
        token = login_response.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        me_url = reverse('accounts:current-user')
        me_response = api_client.get(me_url)
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.data['username'] == 'newuser'


class TestJobApplicationFlow:
    """Integration tests for job application workflow."""
    
    def test_complete_job_application_flow(self, employer_client, authenticated_client, category, employer, user):
        """Test complete flow: create job, apply, update status."""
        # Employer creates a job
        job_url = reverse('jobs:job-list')
        job_data = {
            'title': 'Python Developer',
            'description': 'Looking for Python developer',
            'requirements': '5+ years experience',
            'category': category.id,
            'location': 'Remote',
            'job_type': 'full-time',
            'salary_min': 80000,
            'salary_max': 120000
        }
        job_response = employer_client.post(job_url, job_data, format='json')
        assert job_response.status_code == status.HTTP_201_CREATED
        job_id = job_response.data['id']
        
        # User applies for job
        from django.core.files.uploadedfile import SimpleUploadedFile
        application_url = reverse('applications:application-list')
        resume = SimpleUploadedFile(
            "resume.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        application_data = {
            'job_id': job_id,
            'cover_letter': 'I am interested in this position.',
            'resume': resume
        }
        app_response = authenticated_client.post(application_url, application_data, format='multipart')
        assert app_response.status_code == status.HTTP_201_CREATED
        application_id = app_response.data['id']
        
        # Employer views application
        app_detail_url = reverse('applications:application-detail', kwargs={'pk': application_id})
        app_detail_response = employer_client.get(app_detail_url)
        assert app_detail_response.status_code == status.HTTP_200_OK
        
        # Employer updates application status
        update_data = {'status': 'reviewed', 'notes': 'Under review'}
        update_response = employer_client.patch(app_detail_url, update_data, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data['status'] == 'reviewed'


class TestRoleBasedAccessControl:
    """Integration tests for role-based access control."""
    
    def test_user_cannot_create_job(self, authenticated_client, category):
        """Test that regular users cannot create jobs."""
        url = reverse('job-list')
        data = {
            'title': 'Test Job',
            'description': 'Description',
            'requirements': 'Requirements',
            'category': category.id,
            'location': 'Location'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_employer_cannot_manage_users(self, employer_client):
        """Test that employers cannot manage users."""
        url = reverse('accounts:user-list')
        response = employer_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_full_access(self, admin_client, category, employer):
        """Test that admin has full access."""
        # Can create categories
        cat_url = reverse('categories:category-list')
        cat_response = admin_client.post(cat_url, {'name': 'Admin Category'}, format='json')
        assert cat_response.status_code == status.HTTP_201_CREATED
        
        # Can create jobs
        job_url = reverse('jobs:job-list')
        job_response = admin_client.post(job_url, {
            'title': 'Admin Job',
            'description': 'Description',
            'requirements': 'Requirements',
            'category': category.id,
            'location': 'Location'
        }, format='json')
        assert job_response.status_code == status.HTTP_201_CREATED
        
        # Can manage users
        user_url = reverse('user-list')
        user_response = admin_client.get(user_url)
        assert user_response.status_code == status.HTTP_200_OK


class TestDatabaseConstraints:
    """Integration tests for database constraints."""
    
    def test_unique_together_application(self, application):
        """Test unique_together constraint on application."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.db import IntegrityError
        resume = SimpleUploadedFile(
            "resume2.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        with pytest.raises(IntegrityError):
            Application.objects.create(
                job=application.job,
                applicant=application.applicant,
                cover_letter='Duplicate',
                resume=resume
            )
    
    def test_cascade_delete_job_applications(self, job, application):
        """Test that deleting job cascades to applications."""
        job_id = job.id
        application_id = application.id
        job.delete()
        assert not Application.objects.filter(pk=application_id).exists()
    
    def test_cascade_delete_category_jobs(self, category, job):
        """Test that deleting category cascades to jobs."""
        category_id = category.id
        job_id = job.id
        category.delete()
        assert not Job.objects.filter(pk=job_id).exists()
