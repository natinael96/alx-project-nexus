"""
Custom permissions for jobs app.
"""
from rest_framework import permissions
from .models import Job, Application


class IsJobOwnerOrAdmin(permissions.BasePermission):
    """
    Permission check for job owner or admin.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin:
            return True
        
        # Check if user is the job owner
        if isinstance(obj, Job):
            return obj.employer == request.user
        elif isinstance(obj, Application):
            return obj.job.employer == request.user
        
        return False


class CanApplyForJob(permissions.BasePermission):
    """
    Permission check for job applications.
    Users can apply for active jobs.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated and request.user.is_regular_user
        return True
    
    def has_object_permission(self, request, view, obj):
        # Users can view their own applications
        if request.method in ['GET', 'PATCH', 'PUT']:
            if isinstance(obj, Application):
                return (
                    obj.applicant == request.user or
                    obj.job.employer == request.user or
                    request.user.is_admin
                )
        return False


class CanManageCategory(permissions.BasePermission):
    """
    Permission check for category management (Admin only).
    """
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.is_admin
        return True  # Anyone can view categories

