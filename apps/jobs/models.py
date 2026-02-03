"""
Models for jobs app - Job, Category, and Application.
"""
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from apps.accounts.models import User
from apps.core.utils import validate_file_size, validate_file_extension


class Category(models.Model):
    """
    Category model for organizing jobs by industry/type.
    Supports hierarchical categories with parent-child relationships.
    
    Features:
    - Automatic slug generation from name
    - Hierarchical structure with parent-child relationships
    - Validation to prevent circular references
    - SEO-friendly URLs using slugs
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='Category name (e.g., "Software Development")'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Optional description of the category'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text='Parent category for hierarchical organization'
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        db_index=True,
        help_text='URL-friendly version of the name (auto-generated)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['name', 'parent']),  # Composite index for hierarchical queries
        ]
        # Note: Self-parent validation is handled in clean() method
        # Database constraint would require a function, so we validate in Python
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def clean(self):
        """Validate category data."""
        # Prevent self-parent
        if self.parent == self:
            raise ValidationError({
                'parent': 'A category cannot be its own parent.'
            })
        
        # Prevent circular parent relationships
        if self.parent:
            parent = self.parent
            visited = {self.pk} if self.pk else set()
            
            while parent:
                if parent.pk in visited:
                    raise ValidationError({
                        'parent': 'Circular parent relationship detected. A category cannot be a parent of its own ancestor.'
                    })
                if parent.pk:
                    visited.add(parent.pk)
                parent = parent.parent
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate slug and validate."""
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = self._generate_unique_slug()
        else:
            # Ensure slug is valid even if manually provided
            self.slug = slugify(self.slug)
            if not self.slug:
                self.slug = self._generate_unique_slug()
        
        # Run validation
        self.full_clean()
        super().save(*args, **kwargs)
    
    def _generate_unique_slug(self):
        """Generate a unique slug from the category name."""
        base_slug = slugify(self.name)
        if not base_slug:
            base_slug = 'category'
        
        slug = base_slug
        counter = 1
        
        # Ensure uniqueness
        while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def get_absolute_url(self):
        """Return canonical URL for the category."""
        # Using pk for API consistency (ViewSet uses pk by default)
        # Slug can be used for frontend SEO-friendly URLs
        return reverse('category-detail', kwargs={'pk': self.pk})
    
    def get_full_path(self):
        """Return full hierarchical path (e.g., 'Parent > Child > Grandchild')."""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)
    
    @property
    def depth(self):
        """Return the depth level of this category in the hierarchy."""
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth
    
    def get_descendants(self, include_self=False):
        """Get all descendant categories (children, grandchildren, etc.)."""
        descendants = []
        if include_self:
            descendants.append(self)
        
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        
        return descendants
    
    def get_ancestors(self, include_self=False):
        """Get all ancestor categories (parent, grandparent, etc.)."""
        ancestors = []
        if include_self:
            ancestors.append(self)
        
        parent = self.parent
        while parent:
            ancestors.insert(0, parent)
            parent = parent.parent
        
        return ancestors


class Job(models.Model):
    """
    Job model representing job postings.
    Includes comprehensive job details and status management.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    requirements = models.TextField(help_text='Job requirements and qualifications')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='jobs',
        db_index=True
    )
    employer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_jobs',
        db_index=True
    )
    location = models.CharField(max_length=100, db_index=True)
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default='full-time',
        db_index=True
    )
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Minimum salary'
    )
    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Maximum salary'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    application_deadline = models.DateField(null=True, blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jobs'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']
        indexes = [
            # Composite indexes for common query patterns
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'location']),
            models.Index(fields=['job_type', 'status']),
            models.Index(fields=['salary_min', 'salary_max']),
            models.Index(fields=['is_featured', 'status']),
            # Full-text search index (PostgreSQL)
            GinIndex(fields=['title', 'description'], name='job_search_idx'),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.employer.username}"
    
    def get_absolute_url(self):
        return reverse('job-detail', kwargs={'pk': self.pk})
    
    def increment_views(self):
        """Increment the view count for this job."""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Application(models.Model):
    """
    Application model for job applications.
    Tracks applications submitted by users for jobs.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications',
        db_index=True
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_applications',
        db_index=True
    )
    cover_letter = models.TextField(help_text='Cover letter for the application')
    resume = models.FileField(
        upload_to='resumes/%Y/%m/%d/',
        help_text='Resume file (PDF, DOC, DOCX)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    applied_at = models.DateTimeField(auto_now_add=True, db_index=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Internal notes about the application'
    )
    
    class Meta:
        db_table = 'applications'
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        ordering = ['-applied_at']
        unique_together = [['job', 'applicant']]  # One application per user per job
        indexes = [
            models.Index(fields=['status', '-applied_at']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['applicant', 'status']),
        ]
    
    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"
    
    def get_absolute_url(self):
        return reverse('application-detail', kwargs={'pk': self.pk})
    
    def clean(self):
        """Validate application data."""
        from django.core.exceptions import ValidationError
        
        # Validate resume file
        if self.resume and hasattr(self.resume, 'size'):
            try:
                validate_file_size(self.resume, max_size_mb=5)
                validate_file_extension(self.resume, ['pdf', 'doc', 'docx'])
            except ValidationError as e:
                raise e
        
        # Check if user already applied (only for new applications)
        if self.pk is None and self.job and self.applicant:
            if Application.objects.filter(job=self.job, applicant=self.applicant).exists():
                raise ValidationError('You have already applied for this job.')
    
    def save(self, *args, **kwargs):
        """Override save to run clean validation."""
        self.full_clean()
        super().save(*args, **kwargs)

