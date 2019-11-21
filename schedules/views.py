from rest_framework import generics
from rest_framework import status
from . import serializers
from . import models
import calendar
import datetime
from rest_framework.response import Response
from .utils import get_weeks_of_year
from portal_users.models import Role
from organizations import models as org_models
from portal.local_settings import CURRENT_API


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

        next_week = request.query_params.get('next_week')
        prev_week = request.query_params.get('prev_week')

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
            chosen_date = datetime.datetime.strptime(date_param, '%d.%m.%Y').date()
            weeks = get_weeks_of_year(chosen_date.year)
            week = [w for w in weeks if chosen_date in w][0]

            if next_week:
                index = weeks.index(week)
                try:
                    week = weeks[index + 1]
                except IndexError:  # Next year
                    weeks = get_weeks_of_year(chosen_date.year + 1)
                    if weeks[0][0].year == chosen_date.year:
                        week = weeks[1]
                    else:
                        week = weeks[0]

            elif prev_week:
                index = weeks.index(week)
                try:
                    week = weeks[index - 1]
                except IndexError:  # Previous year
                    weeks = get_weeks_of_year(chosen_date.year - 1)
                    if weeks[-1][-1].year == chosen_date.year:
                        week = weeks[-2]
                    else:
                        week = weeks[-1]
        else:
            """Выбрать текущую дату"""
            chosen_date = datetime.date.today()
            weeks = get_weeks_of_year(chosen_date.year)
            week = [w for w in weeks if chosen_date in w][0]

        work_week = week[:6]  # Without Sunday
        monday = week[0].strftime("%d.%m.%Y")
        saturday = week[5].strftime("%d.%m.%Y")

        # print(current_week)
        resp = dict()
        resp['first_date'] = monday
        resp['last_date'] = saturday

        if my_schedule and my_schedule == '1':
            """Мое расписание"""

            resp['teacher'] = []
            resp['student'] = []
            resp['is_teacher'] = Role.objects.filter(profile=profile,
                                                     is_teacher=True).exists()
            resp['is_student'] = Role.objects.filter(profile=profile,
                                                     is_student=True).exists()

            teacher_lessons = lessons.filter(teacher=profile)

            for day in work_week:
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

                for day in work_week:
                    stud_day_lessons = stud_lessons.filter(date=day).order_by('time__from_time')
                    stud_day = {
                        'date': day.strftime("%d.%m.%Y"),
                        'week_day': 'Понедельник',
                        'periods': self.serializer_class(stud_day_lessons,
                                                         many=True).data
                    }
                    d['lessons'].append(stud_day)
                resp['student'].append(d)
        else:
            resp['days'] = []

            for day in work_week:
                day_lessons = lessons.filter(date=day).order_by('time__from_time')
                d = {
                    'date': day.strftime("%d.%m.%Y"),
                    'week_day': 'Понедельник',
                    'periods': self.serializer_class(day_lessons,
                                                     many=True).data
                }

                resp['days'].append(d)

        resp_wrapper = {
            'next': CURRENT_API + '/schedules/?date={}&next_week=1'.format(monday),
            'prev': CURRENT_API + '/schedules/?date={}&prev_week=1'.format(monday),
            'results': resp
        }

        return Response(
            resp_wrapper,
            status=status.HTTP_200_OK
        )
