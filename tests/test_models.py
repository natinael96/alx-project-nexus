"""
Unit tests for models - Validation, methods, and constraints.
"""
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from apps.accounts.models import User
from apps.jobs.models import Category, Job, Application


class TestCategoryModel:
    """Tests for Category model."""
    
    def test_category_str(self, category):
        """Test category string representation."""
        assert str(category) == category.name
    
    def test_category_str_with_parent(self, category):
        """Test category string representation with parent."""
        child = Category.objects.create(
            name='Child Category',
            parent=category,
            slug='child-category'
        )
        assert '>' in str(child)
    
    def test_category_slug_auto_generation(self, db):
        """Test automatic slug generation."""
        category = Category.objects.create(name='Test Category')
        assert category.slug == 'test-category'
    
    def test_category_slug_uniqueness(self, db, category):
        """Test slug uniqueness."""
        with pytest.raises(ValidationError):
            Category.objects.create(
                name='Different Name',
                slug=category.slug
            )
    
    def test_category_circular_reference_prevention(self, category):
        """Test prevention of circular parent references."""
        child = Category.objects.create(
            name='Child',
            parent=category,
            slug='child'
        )
        category.parent = child
        with pytest.raises(ValidationError):
            category.clean()
    
    def test_category_depth_property(self, category):
        """Test depth property calculation."""
        child = Category.objects.create(
            name='Child',
            parent=category,
            slug='child'
        )
        assert category.depth == 0
        assert child.depth == 1
    
    def test_category_get_full_path(self, category):
        """Test full path generation."""
        child = Category.objects.create(
            name='Child',
            parent=category,
            slug='child'
        )
        path = child.get_full_path()
        assert category.name in path
        assert child.name in path


class TestJobModel:
    """Tests for Job model."""
    
    def test_job_str(self, job):
        """Test job string representation."""
        assert job.employer.username in str(job)
        assert job.title in str(job)
    
    def test_job_increment_views(self, job):
        """Test view count increment."""
        initial_count = job.views_count
        job.increment_views()
        job.refresh_from_db()
        assert job.views_count == initial_count + 1
    
    def test_job_salary_validation(self, employer, category):
        """Test salary range validation."""
        job = Job(
            title='Test Job',
            description='Description',
            requirements='Requirements',
            category=category,
            employer=employer,
            location='Location',
            salary_min=70000,
            salary_max=50000  # Invalid
        )
        with pytest.raises(ValidationError):
            job.clean()
    
    def test_job_application_deadline_validation(self, employer, category):
        """Test application deadline validation."""
        past_date = timezone.now().date() - timedelta(days=1)
        job = Job(
            title='Test Job',
            description='Description',
            requirements='Requirements',
            category=category,
            employer=employer,
            location='Location',
            application_deadline=past_date
        )
        with pytest.raises(ValidationError):
            job.clean()
    
    def test_job_is_accepting_applications_active(self, job):
        """Test is_accepting_applications for active job."""
        job.status = 'active'
        job.application_deadline = None
        job.save()
        assert job.is_accepting_applications is True
    
    def test_job_is_accepting_applications_closed(self, job):
        """Test is_accepting_applications for closed job."""
        job.status = 'closed'
        job.save()
        assert job.is_accepting_applications is False
    
    def test_job_is_accepting_applications_deadline_passed(self, job):
        """Test is_accepting_applications when deadline passed."""
        job.status = 'active'
        job.application_deadline = timezone.now().date() - timedelta(days=1)
        job.save()
        assert job.is_accepting_applications is False
    
    def test_job_days_until_deadline(self, job):
        """Test days_until_deadline calculation."""
        future_date = timezone.now().date() + timedelta(days=5)
        job.application_deadline = future_date
        job.save()
        assert job.days_until_deadline == 5


class TestApplicationModel:
    """Tests for Application model."""
    
    def test_application_str(self, application):
        """Test application string representation."""
        assert application.applicant.username in str(application)
        assert application.job.title in str(application)
    
    def test_application_unique_together(self, application):
        """Test unique_together constraint."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        resume = SimpleUploadedFile(
            "resume2.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        with pytest.raises(Exception):  # IntegrityError or ValidationError
            Application.objects.create(
                job=application.job,
                applicant=application.applicant,
                cover_letter='Another application',
                resume=resume
            )
    
    def test_application_clean_duplicate_prevention(self, application):
        """Test duplicate application prevention in clean."""
        new_app = Application(
            job=application.job,
            applicant=application.applicant,
            cover_letter='Test',
            resume=application.resume
        )
        with pytest.raises(ValidationError):
            new_app.clean()
    
    def test_application_clean_job_status_validation(self, job, user):
        """Test job status validation in clean."""
        job.status = 'closed'
        job.save()
        from django.core.files.uploadedfile import SimpleUploadedFile
        resume = SimpleUploadedFile(
            "resume.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        app = Application(
            job=job,
            applicant=user,
            cover_letter='Test',
            resume=resume
        )
        with pytest.raises(ValidationError):
            app.clean()
    
    def test_application_save_sets_reviewed_at(self, application):
        """Test that reviewed_at is set when status changes."""
        application.status = 'reviewed'
        application.save()
        assert application.reviewed_at is not None
    
    def test_application_file_validation_size(self, job, user):
        """Test file size validation."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        # Create a file larger than 5MB
        large_file = SimpleUploadedFile(
            "large_resume.pdf",
            b"x" * (6 * 1024 * 1024),  # 6MB
            content_type="application/pdf"
        )
        app = Application(
            job=job,
            applicant=user,
            cover_letter='Test',
            resume=large_file
        )
        with pytest.raises(ValidationError):
            app.clean()
    
    def test_application_file_validation_extension(self, job, user):
        """Test file extension validation."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        invalid_file = SimpleUploadedFile(
            "resume.exe",
            b"file_content",
            content_type="application/x-msdownload"
        )
        app = Application(
            job=job,
            applicant=user,
            cover_letter='Test',
            resume=invalid_file
        )
        with pytest.raises(ValidationError):
            app.clean()
