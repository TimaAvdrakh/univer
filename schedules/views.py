from rest_framework import generics
from rest_framework import status
from . import serializers
from . import models
import calendar
import datetime
from rest_framework.response import Response
from .utils import get_weeks_of_year
from portal_users.models import Role, Profile
from organizations import models as org_models
from portal.local_settings import CURRENT_API
from django.utils.translation import gettext as _
from advisors.serializers import GroupShortSerializer
from organizations.serializers import DisciplineSerializer
from portal_users.serializers import ProfileShortSerializer


class TimeWindowListView(generics.ListAPIView):
    """Получить список временных окон"""
    queryset = models.TimeWindow.objects.filter(is_active=True)
    serializer_class = serializers.TimeWindowSerializer


class GroupListView(generics.ListAPIView):
    """Получить все группы"""
    queryset = org_models.Group.objects.filter(is_active=True)
    serializer_class = GroupShortSerializer


class DisciplineListView(generics.ListAPIView):
    """Получить все дисциплины"""
    queryset = org_models.Discipline.objects.filter(is_active=True)
    serializer_class = DisciplineSerializer


class TeacherListView(generics.ListAPIView):
    """Получить всех преподов"""
    queryset = Profile.objects.filter(is_active=True)
    serializer_class = ProfileShortSerializer

    def get_queryset(self):
        teacher_pks = Role.objects.filter(is_teacher=True,
                                          is_active=True).values('profile')
        queryset = self.queryset.filter(pk__in=teacher_pks)
        return queryset


class ClassRoomListView(generics.ListAPIView):
    """Получить все аудитории"""
    queryset = models.Room.objects.filter(is_active=True)
    serializer_class = serializers.RoomSerializer


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
            lessons = lessons.filter(groups__in=[group])

        if discipline:
            lessons = lessons.filter(discipline_id=discipline)

        if teacher:
            lessons = lessons.filter(teachers__in=[teacher])

        if class_room:
            lessons = lessons.filter(classroom_id=class_room)

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

            teacher_lessons = lessons.filter(teachers__in=[profile])

            for day in work_week:
                teacher_day_lessons = teacher_lessons.filter(date=day).order_by('time__from_time')

                time_windows = models.TimeWindow.objects.filter(is_active=True).order_by('from_time')

                window_list = []
                for time_window in time_windows:
                    window_item = {
                        'id': time_window.uid,
                        'name': time_window.name,
                        'start': time_window.from_time,
                        'end': time_window.to_time,
                        'lesson': {},
                    }

                    try:
                        lesson = teacher_day_lessons.get(time=time_window)
                        window_item['lesson'] = self.serializer_class(lesson).data
                    except models.Lesson.DoesNotExist:
                        pass

                    window_list.append(window_item)

                teacher_day = {
                    'date': day.strftime("%d.%m.%Y"),
                    'week_day': _(day.strftime('%A')),
                    'windows': window_list
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
                    'days': []
                }
                stud_lessons = lessons.filter(groups__in=[my_group])

                for day in work_week:
                    stud_day_lessons = stud_lessons.filter(date=day).order_by('time__from_time')

                    time_windows = models.TimeWindow.objects.filter(is_active=True).order_by('from_time')

                    window_list = []
                    for time_window in time_windows:
                        window_item = {
                            'id': time_window.uid,
                            'name': time_window.name,
                            'start': time_window.from_time,
                            'end': time_window.to_time,
                            'lesson': {},
                        }

                        try:
                            lesson = stud_day_lessons.get(time=time_window)
                            window_item['lesson'] = self.serializer_class(lesson).data
                        except models.Lesson.DoesNotExist:
                            pass

                        window_list.append(window_item)

                    stud_day = {
                        'date': day.strftime("%d.%m.%Y"),
                        'week_day': _(day.strftime('%A')),
                        'windows': window_list,
                    }
                    d['days'].append(stud_day)
                resp['student'].append(d)
        else:
            resp['days'] = []

            for day in work_week:
                day_lessons = lessons.filter(date=day).order_by('time__from_time')

                time_windows = models.TimeWindow.objects.filter(is_active=True).order_by('from_time')

                window_list = []
                for time_window in time_windows:
                    window_item = {
                        'id': time_window.uid,
                        'name': time_window.name,
                        'start': time_window.from_time,
                        'end': time_window.to_time,
                        'lesson': {},
                    }

                    try:
                        lesson = day_lessons.get(time=time_window)
                        window_item['lesson'] = self.serializer_class(lesson).data
                    except models.Lesson.DoesNotExist:
                        pass

                    window_list.append(window_item)

                d = {
                    'date': day.strftime("%d.%m.%Y"),
                    'week_day': _(day.strftime('%A')),
                    'windows': window_list
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


class ElJournalListView(generics.ListAPIView):
    """
    Получить список ЭЖ
    discipline, load_type, group
    """
    serializer_class = serializers.ElectronicJournalSerializer
    queryset = models.ElectronicJournal.objects.filter(is_active=True)

    def get_queryset(self):
        profile = self.request.user.profile
        discipline = self.request.query_params.get('discipline')
        load_type = self.request.query_params.get('load_type')  # TODO endpoint
        group = self.request.query_params.get('group')

        queryset = self.queryset.filter(teachers__in=[profile])

        if discipline:
            queryset = queryset.filter(discipline_id=discipline)
        if load_type:
            queryset = queryset.filter(load_type_id=load_type)
        if group:
            queryset = queryset.filter(lesson__groups__in=[group])

        return queryset


class JournalDetailView(generics.RetrieveAPIView):
    # queryset = models.Lesson.objects.filter(is_active=True)

    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        journal_id = request.query_params.get('id')
        next_month = request.query_params.get('next_month')
        prev_month = request.query_params.get('prev_month')
        date_param = request.query_params.get('date')

        journal = models.ElectronicJournal.objects.get(pk=journal_id)
        # lessons = self.queryset.filter(
        #     discipline=journal.discipline,
        #     load_type=journal.load_type,
        #
        # )

        lessons = journal.lessons.filter(
            teachers__in=[profile],
            is_active=True,
        ).order_by('date')

        if date_param:
            """Выбрать дату из параметра"""
            chosen_date = datetime.datetime.strptime(date_param,
                                                     '%d.%m.%Y').date()

            if next_month:
                if chosen_date.month == 12:
                    year = chosen_date.year + 1
                    month = 1
                else:
                    year = chosen_date.year
                    month = chosen_date.month + 1

                days = lessons.filter(
                    date__year=year,
                    date__month=month
                ).distinct('date').values('date')
                date_str = datetime.date(year, month, 1).strftime("%d.%m.%Y")

            elif prev_month:
                if chosen_date.month == 1:
                    year = chosen_date.year - 1
                    month = 12
                else:
                    year = chosen_date.year
                    month = chosen_date.month - 1

                days = lessons.filter(
                    date__year=year,
                    date__month=month,
                ).distinct('date').values('date')

                date_str = datetime.date(year, month, 1).strftime("%d.%m.%Y")

            else:
                month = chosen_date.month
                year = chosen_date.year

                days = lessons.filter(
                    date__year=year,
                    date__month=month,
                ).distinct('date').values('date')

                date_str = chosen_date.strftime("%d.%m.%Y")

        else:
            """Выбрать текущую дату"""
            today = datetime.date.today()
            month = today.month
            year = today.year

            days = lessons.filter(
                date__year=year,
                date__month=month,
            ).distinct('date').values('date')
            date_str = today.strftime("%d.%m.%Y")

        day_list = []
        for day in days:
            day_d = {}
            lessons = lessons.filter(date=day['date'])

            groups = lessons[0].groups.filter(is_active=True)
            student_pks = org_models.StudyPlan.objects.filter(is_active=True,
                                                              group__in=groups).values('student')
            students = Profile.objects.filter(pk__in=student_pks)

            student_list = []
            for student in students:
                stud_d = {}

                lesson_list = []
                for lesson in lessons:
                    lesson_d = {}

                    student_performances = models.StudentPerformance.objects.filter(
                        student=student,
                        lesson=lesson,
                        is_active=True,
                    )

                    if student_performances.exists():
                        try:
                            sp = student_performances.get(mark__grading_system=lesson.grading_system)
                            mark = sp.mark.value_number
                        except models.StudentPerformance.DoesNotExist:
                            sp = student_performances.first()
                            if sp.mark is not None:
                                mark = sp.mark.value_number
                            else:
                                mark = 'H'
                    else:
                        mark = ''

                    lesson_d['lesson_id'] = lesson.uid
                    lesson_d['mark'] = mark
                    lesson_list.append(lesson_d)

                stud_d['lessons'] = lesson_list
                stud_d['student'] = {
                    'id': student.uid,
                    'name': student.full_name,
                }
                student_list.append(stud_d)

            day_d['date'] = day['date'].day
            day_d['students'] = student_list
            day_list.append(day_d)

        resp = {
            'month': _(datetime.date(year=year, month=month, day=1).strftime("%B")),
            'year': year,
            'days': day_list
        }
        resp_wrapper = {
            'next': CURRENT_API + '/schedules/journal/?id={}&date={}&next_month=1'.format(journal_id,
                                                                                          date_str),
            'prev': CURRENT_API + '/schedules/journal/?id={}&date={}&prev_month=1'.format(journal_id,
                                                                                          date_str),
            'results': resp
        }

        return Response(
            resp_wrapper,
            status=status.HTTP_200_OK
        )


