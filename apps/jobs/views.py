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
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CanManageCategory]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @swagger_auto_schema(
        operation_summary='List all categories',
        operation_description='Get a list of all job categories with their children and job counts'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Create a new category',
        operation_description='Create a new job category (Admin only)'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Get category details',
        operation_description='Get detailed information about a specific category'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Update category',
        operation_description='Update a category (Admin only)'
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Delete category',
        operation_description='Delete a category (Admin only)'
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
        """Filter queryset based on user permissions and query parameters."""
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
        operation_description='Get a paginated list of jobs with filtering options'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Get job details',
        operation_description='Get detailed information about a specific job'
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary='Create a new job',
        operation_description='Create a new job posting (Employer/Admin only)',
        request_body=JobCreateUpdateSerializer
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
        operation_description='Update a job posting (Owner/Admin only)',
        request_body=JobCreateUpdateSerializer
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
        operation_description='Delete a job posting (Owner/Admin only)'
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        method='get',
        operation_summary='Get featured jobs',
        operation_description='Get a list of featured/active jobs'
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
        operation_description='Get a list of applications (filtered by user role)'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Get application details',
        operation_description='Get detailed information about a specific application'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Submit job application',
        operation_description='Submit a new job application (User only)',
        request_body=ApplicationSerializer
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
        operation_description='Update application status (Job Owner/Admin only)',
        request_body=ApplicationUpdateSerializer
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

