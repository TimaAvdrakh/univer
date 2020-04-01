from rest_framework import permissions
from portal_users import models as user_models


class AdminPermission(permissions.BasePermission):
    """Доступ у админа универа"""
    def has_permission(self, request, view):
        return user_models.Role.objects.filter(
            profile=request.user.profile,
            is_org_admin=True
        ).exists()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        profile = user.profile
        admin_profile = user_models.Role.objects.filter(
            profile=profile,
            is_org_admin=True
        )
        if admin_profile.exists():
            return True
        elif request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False
