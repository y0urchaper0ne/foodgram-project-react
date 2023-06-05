from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and (
                    request.user.is_admin or request.user.is_superuser)))

    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS 
            or obj.author == request.user):
            return True
