from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAdminOrReadOnlyForAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.method == SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_staff)