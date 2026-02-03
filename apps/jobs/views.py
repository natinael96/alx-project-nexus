"""
Views for jobs app - Job, Category, and Application management.
"""
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Job, Category, Application
from .serializers import (
    JobListSerializer,
    JobDetailSerializer,
    JobCreateUpdateSerializer,
    CategorySerializer,
    ApplicationSerializer,
    ApplicationUpdateSerializer
)
from .filters import JobFilter, ApplicationFilter
from .permissions import IsJobOwnerOrAdmin, CanApplyForJob, CanManageCategory
from apps.accounts.permissions import IsEmployerOrAdmin, IsAdminUser


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category model.
    Admin can create/update/delete, everyone can view.
    
    Features:
    - Hierarchical category structure
    - Automatic slug generation
    - Circular reference prevention
    - SEO-friendly category paths
    """
    queryset = Category.objects.select_related('parent').prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [CanManageCategory]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Optimize queryset with select_related for parent."""
        return super().get_queryset().select_related('parent')
    
    @swagger_auto_schema(
        operation_summary='List all categories',
        operation_description='Get a list of all job categories with their children and job counts. Public read access.',
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description='Search categories by name, description, or slug',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description='Order results by field (name, created_at, -name, -created_at)',
                type=openapi.TYPE_STRING,
                enum=['name', 'created_at', '-name', '-created_at']
            ),
        ],
        responses={
            200: CategorySerializer(many=True),
            401: 'Unauthorized',
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Create a new category',
        operation_description='Create a new job category. Admin only. Validates unique name and slug. Supports parent category assignment for hierarchical structure.',
        request_body=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: 'Bad Request - Validation errors (e.g., duplicate name, circular reference)',
            401: 'Unauthorized',
            403: 'Forbidden - Admin access required',
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Get category details',
        operation_description='Get detailed information about a specific category including children and job count. Public access.',
        responses={
            200: CategorySerializer,
            404: 'Category not found',
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Update category',
        operation_description='Update a category. Admin only. Supports partial updates (PATCH). Validates circular references and unique constraints.',
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: 'Bad Request - Validation errors',
            401: 'Unauthorized',
            403: 'Forbidden - Admin access required',
            404: 'Category not found',
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Delete category',
        operation_description='Delete a category. Admin only. Cascade deletes all child categories and associated jobs.',
        responses={
            204: 'Category deleted successfully',
            401: 'Unauthorized',
            403: 'Forbidden - Admin access required',
            404: 'Category not found',
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Job model.
    Supports CRUD operations with filtering and search.
    """
    queryset = Job.objects.select_related('category', 'employer').prefetch_related('applications')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'requirements', 'location']
    ordering_fields = ['created_at', 'salary_min', 'salary_max', 'views_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return JobListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobDetailSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions and query parameters.
        
        Security:
        - Non-authenticated users see only active jobs
        - Regular users see only active jobs
        - Employers/admins can see all jobs (filtered by status if requested)
        """
        queryset = super().get_queryset()
        
        # By default, show only active jobs to non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='active')
        # Employers and admins can see all their jobs
        elif not (self.request.user.is_employer or self.request.user.is_admin):
            # Regular users see only active jobs
            queryset = queryset.filter(status='active')
        
        return queryset
    
    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ['create']:
            return [IsEmployerOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsJobOwnerOrAdmin()]
        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary='List all jobs',
        operation_description='Get a paginated list of jobs with advanced filtering and search options. Public access (non-authenticated users see only active jobs).',
        manual_parameters=[
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description='Filter by category ID',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'location',
                openapi.IN_QUERY,
                description='Filter by location (case-insensitive partial match)',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'job_type',
                openapi.IN_QUERY,
                description='Filter by job type',
                type=openapi.TYPE_STRING,
                enum=['full-time', 'part-time', 'contract', 'internship', 'freelance']
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Filter by status (authenticated users only)',
                type=openapi.TYPE_STRING,
                enum=['draft', 'active', 'closed']
            ),
            openapi.Parameter(
                'min_salary',
                openapi.IN_QUERY,
                description='Filter by minimum salary (greater than or equal)',
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'max_salary',
                openapi.IN_QUERY,
                description='Filter by maximum salary (less than or equal)',
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'is_featured',
                openapi.IN_QUERY,
                description='Filter featured jobs (true/false)',
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description='Full-text search in title, description, and requirements',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description='Order results by field (created_at, salary_min, salary_max, views_count). Prefix with - for descending.',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='Page number for pagination',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description='Number of items per page (max 100)',
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: JobListSerializer(many=True),
            401: 'Unauthorized',
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Get job details',
        operation_description='Get detailed information about a specific job. Automatically increments view count. Public access for active jobs.',
        responses={
            200: JobDetailSerializer,
            401: 'Unauthorized',
            404: 'Job not found',
        }
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count atomically
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary='Create a new job',
        operation_description='Create a new job posting. Employer/Admin only. Validates salary range (min <= max) and application deadline. Automatically sets employer to current user.',
        request_body=JobCreateUpdateSerializer,
        responses={
            201: JobDetailSerializer,
            400: 'Bad Request - Validation errors',
            401: 'Unauthorized',
            403: 'Forbidden - Employer/Admin access required',
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            JobDetailSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @swagger_auto_schema(
        operation_summary='Update job',
        operation_description='Update a job posting. Job owner/Admin only. Supports partial updates (PATCH). Validates data before saving.',
        request_body=JobCreateUpdateSerializer,
        responses={
            200: JobDetailSerializer,
            400: 'Bad Request - Validation errors',
            401: 'Unauthorized',
            403: 'Forbidden - Job owner/Admin access required',
            404: 'Job not found',
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(JobDetailSerializer(serializer.instance).data)
    
    @swagger_auto_schema(
        operation_summary='Delete job',
        operation_description='Delete a job posting. Job owner/Admin only. Cascade deletes all associated applications.',
        responses={
            204: 'Job deleted successfully',
            401: 'Unauthorized',
            403: 'Forbidden - Job owner/Admin access required',
            404: 'Job not found',
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        method='get',
        operation_summary='Get featured jobs',
        operation_description='Get a list of top 10 featured active jobs. Public access. No pagination (limited results).',
        responses={
            200: JobListSerializer(many=True),
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def featured(self, request):
        """Get featured active jobs."""
        featured_jobs = self.get_queryset().filter(
            is_featured=True,
            status='active'
        )[:10]
        serializer = JobListSerializer(featured_jobs, many=True)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Application model.
    Users can create applications, employers can view/manage applications for their jobs.
    
    Security Features:
    - Role-based access control (Admin/Employer/User)
    - User role required for creating applications
    - Job owner/Admin only for status updates
    - Automatic applicant assignment
    - File validation (size and extension)
    - Duplicate application prevention
    - Job status validation (active jobs only)
    - Status transition validation
    """
    queryset = Application.objects.select_related('job', 'applicant', 'job__employer')
    permission_classes = [IsAuthenticated, CanApplyForJob]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ApplicationFilter
    ordering_fields = ['applied_at', 'status']
    ordering = ['-applied_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['update', 'partial_update']:
            return ApplicationUpdateSerializer
        return ApplicationSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_admin:
            # Admins can see all applications
            return queryset
        elif user.is_employer:
            # Employers can see applications for their jobs
            return queryset.filter(job__employer=user)
        else:
            # Regular users can see only their own applications
            return queryset.filter(applicant=user)
    
    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ['update', 'partial_update']:
            return [IsJobOwnerOrAdmin()]  # Only job owner or admin can update status
        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary='List applications',
        operation_description='Get a paginated list of applications. Results are filtered by user role: Admin sees all, Employer sees applications for their jobs, User sees only their own applications.',
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Filter by application status',
                type=openapi.TYPE_STRING,
                enum=['pending', 'reviewed', 'accepted', 'rejected']
            ),
            openapi.Parameter(
                'job',
                openapi.IN_QUERY,
                description='Filter by job ID',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description='Order results by field (applied_at, status). Prefix with - for descending.',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='Page number for pagination',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description='Number of items per page (max 100)',
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: ApplicationSerializer(many=True),
            401: 'Unauthorized',
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Get application details',
        operation_description='Get detailed information about a specific application. Access is role-based: Users see their own, Employers see applications for their jobs, Admins see all.',
        responses={
            200: ApplicationSerializer,
            401: 'Unauthorized',
            403: 'Forbidden - Access denied',
            404: 'Application not found',
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Submit job application',
        operation_description='Submit a new job application. User role only. Validates: job exists and is active, user hasn\'t already applied, resume file size (max 5MB) and extension (PDF, DOC, DOCX). Automatically sets applicant to current user and status to pending.',
        request_body=ApplicationSerializer,
        responses={
            201: ApplicationSerializer,
            400: 'Bad Request - Validation errors (duplicate application, invalid job, file validation)',
            401: 'Unauthorized',
            403: 'Forbidden - User role required (not employer/admin)',
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @swagger_auto_schema(
        operation_summary='Update application status',
        operation_description='Update application status and notes. Job owner/Admin only. Supports partial updates (PATCH). Automatically sets reviewed_at timestamp when status changes from pending. Validates status transitions.',
        request_body=ApplicationUpdateSerializer,
        responses={
            200: ApplicationUpdateSerializer,
            400: 'Bad Request - Validation errors (invalid status transition)',
            401: 'Unauthorized',
            403: 'Forbidden - Job owner/Admin access required',
            404: 'Application not found',
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

