from rest_framework.permissions import BasePermission
from . import models


class LessonTeacherPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile in obj.teachers.filter(is_active=True)


class ElJournalTeacherPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # return request.user.profile in obj.teachers.filter(is_active=True)

        return models.LessonTeacher.objects.filter(flow_uid=obj.flow_uid,
                                                   teacher=request.user.profile).exists()


