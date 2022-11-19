from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)