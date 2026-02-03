"""
Unit tests for jobs app - Job, Category, and Application management.
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from apps.jobs.models import Category, Job, Application


class TestCategoryEndpoints:
    """Tests for category endpoints."""
    
    def test_list_categories_public_access(self, api_client, category):
        """Test that categories are publicly accessible."""
        url = reverse('categories:category-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_get_category_detail(self, api_client, category):
        """Test getting category details."""
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == category.id
        assert 'children' in response.data
        assert 'job_count' in response.data
    
    def test_create_category_admin_only(self, admin_client):
        """Test that only admins can create categories."""
        url = reverse('categories:category-list')
        data = {
            'name': 'New Category',
            'description': 'Test category'
        }
        response = admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name='New Category').exists()
    
    def test_create_category_non_admin_forbidden(self, authenticated_client):
        """Test that non-admins cannot create categories."""
        url = reverse('categories:category-list')
        data = {'name': 'New Category'}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_category_with_parent(self, admin_client, category):
        """Test creating category with parent."""
        url = reverse('categories:category-list')
        data = {
            'name': 'Sub Category',
            'parent': category.id
        }
        response = admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        sub_category = Category.objects.get(name='Sub Category')
        assert sub_category.parent == category
    
    def test_update_category_admin(self, admin_client, category):
        """Test admin updating category."""
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        data = {'description': 'Updated description'}
        response = admin_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.description == 'Updated description'
    
    def test_delete_category_admin(self, admin_client, category):
        """Test admin deleting category."""
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = admin_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(pk=category.pk).exists()


class TestJobEndpoints:
    """Tests for job endpoints."""
    
    def test_list_jobs_public_access(self, api_client, job):
        """Test that active jobs are publicly accessible."""
        url = reverse('jobs:job-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_list_jobs_only_active_for_public(self, api_client, job, employer):
        """Test that public users only see active jobs."""
        # Create a draft job
        draft_job = Job.objects.create(
            title='Draft Job',
            description='Draft description',
            requirements='Requirements',
            category=job.category,
            employer=employer,
            location='Location',
            status='draft'
        )
        url = reverse('jobs:job-list')
        response = api_client.get(url)
        job_ids = [j['id'] for j in response.data['results']]
        assert job.id in job_ids
        assert draft_job.id not in job_ids
    
    def test_get_job_detail(self, api_client, job):
        """Test getting job details."""
        url = reverse('jobs:job-detail', kwargs={'pk': job.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == job.id
        assert 'has_applied' in response.data
    
    def test_get_job_increments_views(self, api_client, job):
        """Test that viewing job increments view count."""
        initial_views = job.views_count
        url = reverse('jobs:job-detail', kwargs={'pk': job.pk})
        api_client.get(url)
        job.refresh_from_db()
        assert job.views_count == initial_views + 1
    
    def test_create_job_employer(self, employer_client, category, employer):
        """Test employer creating a job."""
        url = reverse('jobs:job-list')
        data = {
            'title': 'New Job',
            'description': 'Job description',
            'requirements': 'Job requirements',
            'category': category.id,
            'location': 'New York',
            'job_type': 'full-time',
            'salary_min': 50000,
            'salary_max': 70000
        }
        response = employer_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        job = Job.objects.get(title='New Job')
        assert job.employer == employer
    
    def test_create_job_non_employer_forbidden(self, authenticated_client, category):
        """Test that non-employers cannot create jobs."""
        url = reverse('jobs:job-list')
        data = {
            'title': 'New Job',
            'description': 'Description',
            'requirements': 'Requirements',
            'category': category.id,
            'location': 'Location'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_job_invalid_salary_range(self, employer_client, category):
        """Test creating job with invalid salary range."""
        url = reverse('jobs:job-list')
        data = {
            'title': 'New Job',
            'description': 'Description',
            'requirements': 'Requirements',
            'category': category.id,
            'location': 'Location',
            'salary_min': 70000,
            'salary_max': 50000  # Invalid: max < min
        }
        response = employer_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_job_owner(self, employer_client, job):
        """Test job owner updating job."""
        url = reverse('jobs:job-detail', kwargs={'pk': job.pk})
        data = {'title': 'Updated Title'}
        response = employer_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        job.refresh_from_db()
        assert job.title == 'Updated Title'
    
    def test_update_job_non_owner_forbidden(self, authenticated_client, job):
        """Test that non-owners cannot update job."""
        url = reverse('jobs:job-detail', kwargs={'pk': job.pk})
        data = {'title': 'Hacked Title'}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_job_owner(self, employer_client, job):
        """Test job owner deleting job."""
        url = reverse('jobs:job-detail', kwargs={'pk': job.pk})
        response = employer_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Job.objects.filter(pk=job.pk).exists()
    
    def test_filter_jobs_by_category(self, api_client, job, category):
        """Test filtering jobs by category."""
        url = reverse('jobs:job-list')
        response = api_client.get(url, {'category': category.id})
        assert response.status_code == status.HTTP_200_OK
        assert all(j['category']['id'] == category.id for j in response.data['results'])
    
    def test_filter_jobs_by_location(self, api_client, job):
        """Test filtering jobs by location."""
        url = reverse('jobs:job-list')
        response = api_client.get(url, {'location': 'New York'})
        assert response.status_code == status.HTTP_200_OK
        assert any('New York' in j['location'] for j in response.data['results'])
    
    def test_filter_jobs_by_salary_range(self, api_client, job):
        """Test filtering jobs by salary range."""
        url = reverse('jobs:job-list')
        response = api_client.get(url, {'min_salary': 70000, 'max_salary': 150000})
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_jobs(self, api_client, job):
        """Test searching jobs."""
        url = reverse('jobs:job-list')
        response = api_client.get(url, {'search': 'Python'})
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_featured_jobs(self, api_client, job):
        """Test getting featured jobs."""
        job.is_featured = True
        job.save()
        url = reverse('jobs:job-featured')  # Custom action from ViewSet
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) <= 10


class TestApplicationEndpoints:
    """Tests for application endpoints."""
    
    def test_create_application_user(self, authenticated_client, job, user):
        """Test user creating an application."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = reverse('applications:application-list')
        resume = SimpleUploadedFile(
            "resume.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        data = {
            'job_id': job.id,
            'cover_letter': 'I am interested in this position.',
            'resume': resume
        }
        response = authenticated_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert Application.objects.filter(job=job, applicant=user).exists()
    
    def test_create_application_duplicate(self, authenticated_client, application):
        """Test that users cannot apply twice for the same job."""
        url = reverse('applications:application-list')
        from django.core.files.uploadedfile import SimpleUploadedFile
        resume = SimpleUploadedFile(
            "resume2.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        data = {
            'job_id': application.job.id,
            'cover_letter': 'Another application',
            'resume': resume
        }
        response = authenticated_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_application_inactive_job(self, authenticated_client, job, user):
        """Test that users cannot apply to inactive jobs."""
        job.status = 'closed'
        job.save()
        url = reverse('applications:application-list')
        from django.core.files.uploadedfile import SimpleUploadedFile
        resume = SimpleUploadedFile(
            "resume.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        data = {
            'job_id': job.id,
            'cover_letter': 'Application',
            'resume': resume
        }
        response = authenticated_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_list_applications_user_sees_own(self, authenticated_client, application, user):
        """Test that users see only their own applications."""
        url = reverse('applications:application-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert all(app['applicant']['id'] == user.id for app in response.data['results'])
    
    def test_list_applications_employer_sees_job_applications(self, employer_client, application, job):
        """Test that employers see applications for their jobs."""
        url = reverse('applications:application-list')
        response = employer_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert any(app['job']['id'] == job.id for app in response.data['results'])
    
    def test_update_application_status_employer(self, employer_client, application):
        """Test employer updating application status."""
        url = reverse('applications:application-detail', kwargs={'pk': application.pk})
        data = {'status': 'reviewed', 'notes': 'Under review'}
        response = employer_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        application.refresh_from_db()
        assert application.status == 'reviewed'
        assert application.reviewed_at is not None
    
    def test_update_application_status_invalid_transition(self, employer_client, application):
        """Test invalid status transition."""
        application.status = 'accepted'
        application.save()
        url = reverse('applications:application-detail', kwargs={'pk': application.pk})
        data = {'status': 'pending'}  # Cannot go back from accepted
        response = employer_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_application_non_owner_forbidden(self, authenticated_client, application):
        """Test that non-owners cannot update application status."""
        url = reverse('applications:application-detail', kwargs={'pk': application.pk})
        data = {'status': 'accepted'}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
