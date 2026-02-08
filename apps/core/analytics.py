"""
Analytics and statistics utilities.
"""
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.jobs.models import Job, Application, Category
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for generating analytics and statistics.
    """
    
    @staticmethod
    def get_user_statistics():
        """Get user statistics."""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        users_by_role = User.objects.values('role').annotate(count=Count('id'))
        
        # Recent registrations (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_registrations = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'users_by_role': {item['role']: item['count'] for item in users_by_role},
            'recent_registrations_30d': recent_registrations,
        }
    
    @staticmethod
    def get_job_statistics():
        """Get job statistics."""
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(status='active').count()
        jobs_by_status = Job.objects.values('status').annotate(count=Count('id'))
        jobs_by_type = Job.objects.values('job_type').annotate(count=Count('id'))
        
        # Recent jobs (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_jobs = Job.objects.filter(created_at__gte=thirty_days_ago).count()
        
        # Featured jobs
        featured_jobs = Job.objects.filter(is_featured=True, status='active').count()
        
        # Total views
        total_views = Job.objects.aggregate(total=Sum('views_count'))['total'] or 0
        
        # Average views per job
        avg_views = Job.objects.aggregate(avg=Avg('views_count'))['avg'] or 0
        
        return {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'jobs_by_status': {item['status']: item['count'] for item in jobs_by_status},
            'jobs_by_type': {item['job_type']: item['count'] for item in jobs_by_type},
            'recent_jobs_30d': recent_jobs,
            'featured_jobs': featured_jobs,
            'total_views': total_views,
            'average_views_per_job': round(avg_views, 2),
        }
    
    @staticmethod
    def get_application_statistics():
        """Get application statistics."""
        total_applications = Application.objects.count()
        applications_by_status = Application.objects.values('status').annotate(count=Count('id'))
        
        # Recent applications (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_applications = Application.objects.filter(applied_at__gte=thirty_days_ago).count()
        
        # Average applications per job
        avg_applications = Job.objects.annotate(
            app_count=Count('applications')
        ).aggregate(avg=Avg('app_count'))['avg'] or 0
        
        # Jobs with most applications
        top_jobs = Job.objects.annotate(
            app_count=Count('applications')
        ).order_by('-app_count')[:5].values('id', 'title', 'app_count')
        
        return {
            'total_applications': total_applications,
            'applications_by_status': {item['status']: item['count'] for item in applications_by_status},
            'recent_applications_30d': recent_applications,
            'average_applications_per_job': round(avg_applications, 2),
            'top_jobs_by_applications': list(top_jobs),
        }
    
    @staticmethod
    def get_category_statistics():
        """Get category statistics."""
        total_categories = Category.objects.count()
        categories_with_jobs = Category.objects.annotate(
            job_count=Count('jobs')
        ).filter(job_count__gt=0).count()
        
        # Top categories by job count
        top_categories = Category.objects.annotate(
            job_count=Count('jobs')
        ).order_by('-job_count')[:10].values('id', 'name', 'job_count')
        
        return {
            'total_categories': total_categories,
            'categories_with_jobs': categories_with_jobs,
            'top_categories': list(top_categories),
        }
    
    @staticmethod
    def get_overall_statistics():
        """Get comprehensive statistics."""
        return {
            'users': AnalyticsService.get_user_statistics(),
            'jobs': AnalyticsService.get_job_statistics(),
            'applications': AnalyticsService.get_application_statistics(),
            'categories': AnalyticsService.get_category_statistics(),
            'timestamp': timezone.now().isoformat(),
        }
    
    @staticmethod
    def get_user_activity(user_id, days=30):
        """Get activity statistics for a specific user."""
        user = User.objects.get(id=user_id)
        cutoff_date = timezone.now() - timedelta(days=days)
        
        if user.is_employer:
            # Employer activity
            jobs_posted = Job.objects.filter(employer=user, created_at__gte=cutoff_date).count()
            applications_received = Application.objects.filter(
                job__employer=user,
                applied_at__gte=cutoff_date
            ).count()
            
            return {
                'user_id': user_id,
                'user_type': 'employer',
                'jobs_posted': jobs_posted,
                'applications_received': applications_received,
                'period_days': days,
            }
        else:
            # Regular user activity
            applications_submitted = Application.objects.filter(
                applicant=user,
                applied_at__gte=cutoff_date
            ).count()
            
            return {
                'user_id': user_id,
                'user_type': 'user',
                'applications_submitted': applications_submitted,
                'period_days': days,
            }
