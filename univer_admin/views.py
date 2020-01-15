from rest_framework import generics
from schedules import models as sh_models
from . import serializers
from rest_framework.response import Response
from rest_framework import status
from . import permissions
from rest_framework.permissions import IsAuthenticated
from schedules import serializers as sh_serializers
from datetime import datetime
from portal_users.utils import get_current_study_year
from common.paginators import CustomPagination
from organizations import models as org_models
from advisors.serializers import CathedraSerializer


class HandleLessonView(generics.CreateAPIView):
    """Открыть/закрыть выбранное занятие"""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    serializer_class = serializers.HandleLessonSerializer


class HandleJournalView(generics.CreateAPIView):
    """Закрыть/Открыть Журнал"""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    serializer_class = serializers.HandleJournalSerializer


class JournalLessonListView(generics.ListAPIView):
    """Список занятии выбранного Журнала
    journal, date"""
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


def get_curr_study_year_obj():
    """Возвращает объект текущего уч года (StudyPeriod)"""
    d = get_current_study_year()

    try:
        study_year = org_models.StudyPeriod.objects.get(start=d['start'],
                                                        end=d['end'])
    except org_models.StudyPeriod.DoesNotExist:
        study_year = None

    return study_year


class JournalListView(generics.ListAPIView):  # TODO continue
    """Получить список ЭЖ для блокировки для Админа
       Поиск: study_year, cathedra, teacher, discipline"""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    queryset = sh_models.ElectronicJournal.objects.filter(is_active=True)
    serializer_class = sh_serializers.ElectronicJournalSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        study_year = self.request.query_params.get('study_year')
        cathedra = self.request.query_params.get('cathedra')
        teacher = self.request.query_params.get('teacher')
        discipline = self.request.query_params.get('discipline')

        queryset = self.queryset.all().order_by('discipline__name')
        if discipline:
            queryset = queryset.filter(discipline_id=discipline)

        if teacher:
            # queryset = queryset.filter(lessons__teachers__in=[teacher])
            flow_uids = sh_models.LessonTeacher.objects.filter(teacher_id=teacher,
                                                               is_active=True).values('flow_uid')
            queryset = queryset.filter(flow_uid__in=flow_uids)

        if study_year:
            queryset = queryset.filter(study_year_id=study_year)
        else:
            curr_study_year = get_curr_study_year_obj()
            if curr_study_year is not None:
                queryset = queryset.filter(study_year=curr_study_year)

        return queryset


class CathedraListView(generics.ListAPIView):
    """Получить список кафедр"""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    queryset = org_models.Cathedra.objects.filter(is_active=True).order_by('name')
    serializer_class = CathedraSerializer


class CancelPlanBlockView(generics.CreateAPIView):  # TODO
    """Отменить запланированную блокировку"""
    permission_classes = (
        IsAuthenticated,
        permissions.AdminPermission,
    )
    serializer_class = serializers.CancelPlanBlockSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'message': 'ok'
            },
            status=status.HTTP_200_OK
        )


