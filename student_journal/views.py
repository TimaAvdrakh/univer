from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from schedules import models as sh_models
from organizations import models as org_models
from django.db.models import Avg
from common.paginators import CustomPagination
from organizations.serializers import DisciplineSerializer


class MyPerformanceView(generics.RetrieveAPIView):
    """Моя успеваемость
    study_year, acad_period, discipline"""
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        study_year = request.query_params.get('study_year')
        acad_period = request.query_params.get('acad_period')
        discipline = request.query_params.get('discipline')

        flow_uids = sh_models.LessonStudent.objects.filter(
            student=profile,
            is_active=True).distinct('flow_uid').values('flow_uid')

        filter_dict = {
            "flow_uid__in": flow_uids,
            "is_active": True,
        }
        if study_year:
            filter_dict["study_year_id"] = study_year
        if acad_period:
            filter_dict["acad_period_id"] = acad_period
        if discipline:
            filter_dict["discipline_id"] = discipline

        discipline_pks = sh_models.Lesson.objects.filter(**filter_dict). \
            distinct('discipline'). \
            values('discipline')

        disciplines = org_models.Discipline.objects.filter(pk__in=discipline_pks,
                                                           is_active=True)

        resp = []
        for disc in disciplines:
            item = {}
            sps = sh_models.StudentPerformance.objects.filter(lesson__discipline=disc,
                                                              student=profile,
                                                              is_active=True)
            missed_count = sps.filter(missed=True).count()

            av_curr_mark = sps.filter(mark__isnull=False).aggregate(avg=Avg('mark__weight'))['avg']

            item['disc_uid'] = disc.uid
            item['discipline'] = disc.name
            item['missed_count'] = missed_count
            item['av_curr_mark'] = av_curr_mark or ''
            item['itog_curr_mark'] = av_curr_mark * 0.6 if av_curr_mark is not None else ''
            item['disciplines'] = []
            item['getSubjects'] = False
            resp.append(item)

        page = self.paginate_queryset(resp)
        if page is not None:

            return self.get_paginated_response(page)


class DisciplinePerformanceDetailView(generics.RetrieveAPIView):
    """Детальная инфо об успеваемости по выбранной дисциплине"""

    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        discipline = request.query_params.get('discipline')

        sps = sh_models.StudentPerformance.objects.filter(
            lesson__discipline_id=discipline,
            student=profile,
            is_active=True,
        )
        lessons = []
        for item in sps:
            lesson = {
                'subject': item.lesson.subject,
                'date': item.lesson.date,
                'mark': item.mark.weight if item.mark else '',
                'missed': 'H' if item.missed else '',
                'load_type': item.lesson.load_type.name,
            }
            lessons.append(lesson)

        return Response(
            lessons,
            status=status.HTTP_200_OK
        )


class DisciplineListView(generics.ListAPIView):
    """Получить мои дисциплины для ЭЖ"""
    queryset = org_models.Discipline.objects.filter(is_active=True)
    serializer_class = DisciplineSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        study_year = self.request.query_params.get('study_year')
        acad_period = self.request.query_params.get('acad_period')

        filter_d = {
            'student': profile,
            'is_active': True
        }

        if study_year:
            filter_d['study_year_id'] = study_year
        if acad_period:
            filter_d['acad_period_id'] = acad_period

        discipline_pks = org_models.StudentDiscipline.objects.filter(**filter_d).values('discipline')

        queryset = self.queryset.filter(pk__in=discipline_pks)

        return queryset

