from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    request user must be owner of the object
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user