from rest_framework import generics
from schedules import models as sh_models
from . import serializers
from rest_framework.response import Response
from rest_framework import status
from . import permissions
from rest_framework.permissions import IsAuthenticated
from schedules import serializers as sh_serializers
from datetime import datetime


class HandleLessonView(generics.UpdateAPIView):
    """Открыть/закрыть выбранное занятие, urlparam=uid занятия"""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    queryset = sh_models.Lesson.objects.filter(is_active=True)
    serializer_class = serializers.HandleLessonSerializer


class JournalLessonListView(generics.ListAPIView):  # TODO continue
    """Список занятии выбранного Журнала"""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    queryset = sh_models.Lesson.objects.filter(is_active=True)
    serializer_class = sh_serializers.LessonShortSerializer

    def get_queryset(self):
        journal_id = self.request.query_params.get('journal')
        date = self.request.query_params.get('date')
        queryset = self.queryset.filter(el_journal_id=journal_id)
        if date:
            chosen_date = datetime.strptime(date,
                                            '%d.%m.%Y').date()
            queryset = queryset.filter(date=chosen_date)

        return queryset


class HandleJournalView(generics.UpdateAPIView):
    """Закрыть/Открыть Журнал"""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    queryset = sh_models.ElectronicJournal.objects.filter(is_active=True)
    serializer_class = serializers.HandleJournalSerializer


# class PlanJournalCloseView(generics.UpdateAPIView):
#     """Планировать закрытие Журнал"""
#     permission_classes = (
#         IsAuthenticated,
#         permissions.AdminPermission,
#     )
#     queryset = sh_models.ElectronicJournal.objects.filter(is_active=True)
#     serializer_class = serializers.HandleJournalSerializer


class EJournalsView(generics.ListAPIView):
    """ Поиск по преподавателям, по дисциплинам,
    по кафедрам, по образовательным программам, по уровню образования,
    по форме образования и по учебным годам."""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    queryset = sh_models.ElectronicJournal.objects.filter(is_active=True)
    serializer_class = sh_serializers.ElectronicJournalSerializer

    def get_queryset(self):
        profile = self.request.user.profile

        teacher = self.request.query_params.get('teacher')
        discipline = self.request.query_params.get('discipline')
        cathedra = self.request.query_params.get('cathedra')
        op = self.request.query_params.get('op')
        prep_level = self.request.query_params.get('prep_level')
        study_form = self.request.query_params.get('study_form')
        study_year = self.request.query_params.get('study_year')

        queryset = self.queryset.all()
        if discipline:
            queryset = queryset.filter(discipline_id=discipline)
        if teacher:
            queryset = queryset.filter(lessons__teachers__in=[teacher])
        if study_year:
            queryset = queryset.filter(lessons__study_year_id=study_year)
