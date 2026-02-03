"""
Custom permissions for accounts app.
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission check for admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsEmployerOrAdmin(permissions.BasePermission):
    """
    Permission check for employer or admin users.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_employer or request.user.is_admin)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission check for object owner or admin.
    
    Security: Checks authentication before accessing user properties
    to prevent AttributeError and ensure proper authorization.
    """
    def has_object_permission(self, request, view, obj):
        # Check authentication first
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin can do anything
        if request.user.is_admin:
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'employer'):
            return obj.employer == request.user
        elif hasattr(obj, 'applicant'):
            return obj.applicant == request.user
        
        return False

