from rest_framework.permissions import BasePermission


class StudentDisciplinePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.student == request.user.profile


class StudyPlanPermission(BasePermission):
    """Доступ у студента учебного плана"""
    def has_object_permission(self, request, view, obj):
        return obj.student == request.user.profile
