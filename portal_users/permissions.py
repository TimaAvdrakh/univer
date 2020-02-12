from rest_framework.permissions import BasePermission


class StudentDisciplinePermission(BasePermission):
    """Выбирает препода сам студент или его эдвайзер"""
    def has_object_permission(self, request, view, obj):
        if obj.student == request.user.profile:
            return True

        if obj.study_plan.advisor == request.user.profile:
            return True


class StudyPlanPermission(BasePermission):
    """Доступ у студента учебного плана и у эдвайзера"""
    def has_object_permission(self, request, view, obj):
        if obj.student == request.user.profile:
            return True

        if obj.advisor == request.user.profile:
            return True


class ProfilePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile == obj


class DisciplineCreditPermission(BasePermission):
    """Выбирает формы контроля сам студент или его эдвайзер"""
    def has_object_permission(self, request, view, obj):
        if obj.student == request.user.profile:
            return True

        if obj.study_plan.advisor == request.user.profile:
            return True
