from rest_framework.permissions import BasePermission
from portal_users import models as user_models


class AdminPermission(BasePermission):
    """Доступ у админа универа"""
    def has_permission(self, request, view):
        return user_models.Role.objects.filter(profile=request.user.profile,
                                               is_org_admin=True).exists()
