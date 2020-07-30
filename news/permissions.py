from rest_framework.permissions import DjangoModelPermissions, SAFE_METHODS


class NewsPermission(DjangoModelPermissions):
    def has_permission(self, request, view):
        profile = request.user.profile
        if profile.role.is_columnist:
            return True
        elif request.method in SAFE_METHODS:
            return True
        else:
            return False
