from rest_framework.permissions import BasePermission


class StudyPlanAdvisorPermission(BasePermission):
    """Доступ у эдвайзера учебного плана"""

    def has_object_permission(self, request, view, obj):
        if obj.advisor == request.user.profile:
            return True


class StudentDisciplinePermission(BasePermission):
    """Доступ у эдвайзера"""
    def has_object_permission(self, request, view, obj):
        if obj.study_plan.advisor == request.user.profile:
            return True
