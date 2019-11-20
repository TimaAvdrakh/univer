from rest_framework import generics
from rest_framework import status
from . import serializers
from . import models
import calendar
from datetime import date
from rest_framework.response import Response
from .utils import weeks_of_year
from portal_users.models import Role
from organizations import models as org_models


class TimeWindowListView(generics.ListAPIView):
    """Получить список временных окон"""
    queryset = models.TimeWindow.objects.filter(is_active=True)
    serializer_class = serializers.TimeWindowSerializer


class ScheduleListView(generics.ListAPIView):
    """Получить расписание
    group, discipline, teacher, class_room, date, my
    """
    queryset = models.Lesson.objects.filter(is_active=True)
    serializer_class = serializers.LessonSerializer

    def list(self, request, *args, **kwargs):
        profile = request.user.profile

        group = request.query_params.get('group')
        discipline = request.query_params.get('discipline')
        teacher = request.query_params.get('teacher')
        class_room = request.query_params.get('class_room')
        date_param = request.query_params.get('date')
        my_schedule = request.query_params.get('my')  # my=1 Мое расписание

        lessons = self.queryset.all()

        if group:
            lessons = lessons.filter(group__in=group)

        if discipline:
            lessons = lessons.filter(discipline_id=discipline)

        if teacher:
            lessons = lessons.filter(teacher_id=teacher)

        if class_room:
            lessons = lessons.filter(class_room_id=class_room)

        if date_param:
            """Выбрать дату из параметра"""
            chosen_date = date.today()  # TODO get date from date_param
        else:
            """Выбрать текущую дату"""
            chosen_date = date.today()

        weeks = weeks_of_year(date.today().year)
        week = [w for w in weeks if chosen_date in w]
        monday = week[0][0].strftime("%d.%m.%Y")
        sunday = week[0][5].strftime("%d.%m.%Y")

        # print(current_week)
        resp = dict()
        resp['first_date'] = monday
        resp['last_date'] = sunday

        if my_schedule and my_schedule == '1':
            """Мое расписание"""

            resp['teacher'] = []
            resp['student'] = []
            resp['is_teacher'] = True
            resp['is_student'] = True

            teacher_lessons = lessons.filter(teacher=profile)

            for day in week[0][:6]:
                teacher_day_lessons = teacher_lessons.filter(date=day).order_by('time__from_time')
                teacher_day = {
                    'date': day.strftime("%d.%m.%Y"),
                    'week_day': 'Понедельник',
                    'periods': self.serializer_class(teacher_day_lessons,
                                                     many=True).data
                }
                resp['teacher'].append(teacher_day)

            my_group_pks = org_models.StudyPlan.objects.filter(
                student=profile,
                is_active=True,
            ).values('group')
            my_groups = org_models.Group.objects.filter(pk__in=my_group_pks)

            for my_group in my_groups:
                d = {
                    'group': my_group.name,
                    'lessons': []
                }
                stud_lessons = lessons.filter(groups__in=[my_group])

                for day in week[0][:6]:
                    stud_day_lessons = stud_lessons.filter(date=day).order_by('time__from_time')
                    stud_day = {
                        'date': day.strftime("%d.%m.%Y"),
                        'periods': self.serializer_class(stud_day_lessons,
                                                         many=True).data
                    }
                    d['lessons'].append(stud_day)
                resp['student'].append(d)
        else:
            resp['days'] = []

            for day in week[0][:6]:
                day_lessons = lessons.filter(date=day).order_by('time__from_time')
                d = {
                    'date': day.strftime("%d.%m.%Y"),
                    'week_day': 'Понедельник',
                    'periods': self.serializer_class(day_lessons,
                                                     many=True).data
                }

                resp['days'].append(d)

        return Response(
            resp,
            status=status.HTTP_200_OK
        )
