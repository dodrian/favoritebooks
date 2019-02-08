from rest_framework import permissions


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, object):
        if request.method in permissions.SAFE_METHODS or request.user.is_staff:
            return True
        return object.user == request.user


class IsSelforAdminorReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, object):
        if request.method in permissions.SAFE_METHODS or request.user.is_staff:
            return True
        return object == request.user
