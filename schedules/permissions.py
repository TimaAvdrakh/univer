from rest_framework.permissions import BasePermission


class TeacherPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile in obj.teachers.filter(is_active=True)
