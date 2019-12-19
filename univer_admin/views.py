from rest_framework import generics
from schedules import models as sh_models
from . import serializers
from rest_framework.response import Response
from rest_framework import status
from . import permissions
from rest_framework.permissions import IsAuthenticated


class AllowMarkLessonView(generics.UpdateAPIView):
    """Разрешить оценивать выбранное занятие, urlparam=uid занятия"""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    queryset = sh_models.Lesson.objects.filter(is_active=True)
    serializer_class = serializers.AllowMarkLessonSerializer


class JournalLessonListView(generics.ListAPIView):
    pass

