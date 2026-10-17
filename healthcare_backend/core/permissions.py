"""
Custom DRF permissions for CareOS.
"""
from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access or edit it.
    Assumes the model instance has a `created_by` attribute.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check created_by or assigned_by or user
        owner = getattr(obj, 'created_by', None)
        if owner is not None:
            return owner == request.user
        
        assigned_by = getattr(obj, 'assigned_by', None)
        if assigned_by is not None:
            return assigned_by == request.user
            
        return False


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Allow any authenticated user to view (GET, HEAD, OPTIONS),
    but only the creator can update or delete.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        owner = getattr(obj, 'created_by', None)
        return owner == request.user
