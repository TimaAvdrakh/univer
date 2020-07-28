from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class SupervisorViewPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.profile.role.is_supervisor and request.method in SAFE_METHODS:
            return True
        else:
            return False
