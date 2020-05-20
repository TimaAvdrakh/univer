from rest_framework.permissions import BasePermission
from portal_users import models as user_models
from rest_framework import permissions


class AdminPermission(BasePermission):
    """Доступ у админа универа"""
    def has_permission(self, request, view):
        return user_models.Role.objects.filter(
            profile=request.user.profile,
            is_org_admin=True
        ).exists()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if hasattr(user, 'profile'):
            is_admin = user_models.Role.objects.filter(profile=user.profile, is_org_admin=True).exists()
            # Админы организаций могут создавать любые объекты
            if is_admin:
                return True
            # Пользователи (аноны и системные) просто получать эти объекты
            elif request.method in permissions.SAFE_METHODS:
                return True
            else:
                return False
        elif request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False
