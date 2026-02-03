"""
Serializers for jobs app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Job, Category, Application

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    children = serializers.SerializerMethodField()
    job_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    depth = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'parent', 'slug',
            'children', 'job_count', 'full_path', 'depth',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at', 'depth')
        extra_kwargs = {
            'name': {'required': True},
        }
    
    def get_children(self, obj):
        """Get child categories."""
        children = obj.children.all()
        return CategorySerializer(children, many=True).data if children.exists() else []
    
    def get_job_count(self, obj):
        """Get count of active jobs in this category."""
        return obj.jobs.filter(status='active').count()
    
    def get_full_path(self, obj):
        """Get full hierarchical path."""
        return obj.get_full_path()
    
    def validate_parent(self, value):
        """Validate parent category."""
        if value:
            # Prevent setting parent to self (will be caught in model clean, but check here too)
            if self.instance and value.pk == self.instance.pk:
                raise serializers.ValidationError('A category cannot be its own parent.')
        return value


class JobListSerializer(serializers.ModelSerializer):
    """Serializer for listing jobs (lightweight)."""
    category = CategorySerializer(read_only=True)
    employer = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = (
            'id', 'title', 'description', 'category', 'employer',
            'location', 'job_type', 'salary_min', 'salary_max',
            'status', 'is_featured', 'views_count', 'application_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'views_count')
    
    def get_employer(self, obj):
        """Get employer information."""
        return {
            'id': obj.employer.id,
            'username': obj.employer.username,
            'email': obj.employer.email
        }
    
    def get_application_count(self, obj):
        """Get count of applications for this job."""
        return obj.applications.count()


class JobDetailSerializer(serializers.ModelSerializer):
    """Serializer for job details (full information)."""
    category = CategorySerializer(read_only=True)
    employer = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = (
            'id', 'title', 'description', 'requirements', 'category',
            'employer', 'location', 'job_type', 'salary_min', 'salary_max',
            'status', 'application_deadline', 'is_featured', 'views_count',
            'application_count', 'has_applied', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'views_count',
            'application_count', 'has_applied'
        )
    
    def get_employer(self, obj):
        """Get employer information."""
        return {
            'id': obj.employer.id,
            'username': obj.employer.username,
            'email': obj.employer.email
        }
    
    def get_application_count(self, obj):
        """Get count of applications for this job."""
        return obj.applications.count()
    
    def get_has_applied(self, obj):
        """Check if current user has applied for this job."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.applications.filter(applicant=request.user).exists()
        return False


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating jobs."""
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    
    class Meta:
        model = Job
        fields = (
            'title', 'description', 'requirements', 'category',
            'location', 'job_type', 'salary_min', 'salary_max',
            'status', 'application_deadline', 'is_featured'
        )
    
    def validate(self, attrs):
        """Validate job data."""
        salary_min = attrs.get('salary_min')
        salary_max = attrs.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError({
                'salary_max': 'Maximum salary must be greater than minimum salary.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create a new job."""
        validated_data['employer'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Application model."""
    job = JobListSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.filter(status='active'),
        source='job',
        write_only=True
    )
    applicant = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = (
            'id', 'job', 'job_id', 'applicant', 'cover_letter',
            'resume', 'status', 'applied_at', 'reviewed_at', 'notes'
        )
        read_only_fields = (
            'id', 'applicant', 'applied_at', 'reviewed_at', 'status'
        )
    
    def get_applicant(self, obj):
        """Get applicant information."""
        return {
            'id': obj.applicant.id,
            'username': obj.applicant.username,
            'email': obj.applicant.email
        }
    
    def validate(self, attrs):
        """Validate application data."""
        request = self.context.get('request')
        job = attrs.get('job')
        
        if not job:
            return attrs
        
        # Check if user already applied
        if request and request.user.is_authenticated:
            if Application.objects.filter(job=job, applicant=request.user).exists():
                raise serializers.ValidationError({
                    'job': 'You have already applied for this job.'
                })
            
            # Validate job is accepting applications
            if not job.is_accepting_applications:
                if job.status != 'active':
                    raise serializers.ValidationError({
                        'job': f'Cannot apply to a {job.get_status_display().lower()} job.'
                    })
                elif job.application_deadline and job.application_deadline < timezone.now().date():
                    raise serializers.ValidationError({
                        'job': 'Application deadline has passed.'
                    })
        
        return attrs
    
    def create(self, validated_data):
        """Create a new application."""
        validated_data['applicant'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating application status (employer/admin only).
    
    Security: Only allows updating status and notes.
    Automatically sets reviewed_at when status changes.
    """
    class Meta:
        model = Application
        fields = ('status', 'notes', 'reviewed_at')
        read_only_fields = ('reviewed_at',)
    
    def validate_status(self, value):
        """Validate status transition."""
        if self.instance:
            current_status = self.instance.status
            # Define valid status transitions
            valid_transitions = {
                'pending': ['reviewed', 'accepted', 'rejected'],
                'reviewed': ['accepted', 'rejected'],
                'accepted': [],  # Final state
                'rejected': [],  # Final state
            }
            
            # Check if transition is valid
            if value != current_status:
                if value not in valid_transitions.get(current_status, []):
                    raise serializers.ValidationError(
                        f'Cannot transition from {current_status} to {value}. '
                        f'Valid transitions: {", ".join(valid_transitions.get(current_status, []))}'
                    )
        
        return value
    
    def update(self, instance, validated_data):
        """Update application and set reviewed_at if status changes."""
        # Update reviewed_at when status changes from pending
        if 'status' in validated_data and instance.status != validated_data['status']:
            if instance.status == 'pending' and not instance.reviewed_at:
                validated_data['reviewed_at'] = timezone.now()
        
        return super().update(instance, validated_data)

