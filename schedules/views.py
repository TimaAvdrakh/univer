from rest_framework import generics
from rest_framework import status
from . import serializers
from . import models
import calendar
import datetime
from rest_framework.response import Response
from .utils import get_weeks_of_year, lesson_change_access
from portal_users.models import Role, Profile, TeacherPosition
from organizations import models as org_models
from portal.local_settings import CURRENT_API
from django.utils.translation import gettext as _
from advisors.serializers import GroupShortSerializer
from organizations.serializers import DisciplineSerializer
from portal_users.serializers import ProfileShortSerializer
from rest_framework.permissions import IsAuthenticated
from . import permissions
from django.db.models import Avg, Q
import json


class TimeWindowListView(generics.ListAPIView):
    """Получить список временных окон"""
    queryset = models.TimeWindow.objects.filter(is_active=True)
    serializer_class = serializers.TimeWindowSerializer


class GroupListView(generics.ListAPIView):
    """Получить все группы"""
    queryset = org_models.Group.objects.filter(is_active=True)
    serializer_class = GroupShortSerializer


class LoadType2ListView(generics.ListAPIView):
    """Получить все типы нагрузки"""
    queryset = org_models.LoadType2.objects.filter(is_active=True)
    serializer_class = serializers.LoadType2Serializer


class DisciplineListView(generics.ListAPIView):
    """Получить все дисциплины
    study_year, teacher"""
    queryset = org_models.Discipline.objects.filter(is_active=True)
    serializer_class = DisciplineSerializer

    def get_queryset(self):
        study_year = self.request.query_params.get('study_year')
        teacher = self.request.query_params.get('teacher')

        queryset = self.queryset.all().order_by('name')

        filter_d = {
            'is_active': True,
        }

        if study_year:
            filter_d['study_period_id'] = study_year
        if teacher:
            filter_d['teacher_id'] = teacher

        if study_year or teacher:
            disc_pks = org_models.TeacherDiscipline.objects.filter(**filter_d).values('discipline')
            queryset = queryset.filter(pk__in=disc_pks)

        return queryset


class TeacherListView(generics.ListAPIView):
    """Получить всех преподов.
    cathedra, study_year"""
    queryset = Profile.objects.filter(is_active=True)
    serializer_class = ProfileShortSerializer

    def get_queryset(self):
        study_year = self.request.query_params.get('study_year')
        cathedra = self.request.query_params.get('cathedra')

        teacher_pks = Role.objects.filter(is_teacher=True,
                                          is_active=True).values('profile')
        queryset = self.queryset.filter(pk__in=teacher_pks).order_by('last_name',
                                                                     'first_name',
                                                                     'middle_name')

        filter_d = {
            'is_active': True
        }
        if study_year:
            filter_d['study_year_id'] = study_year

        if cathedra:
            filter_d['cathedra_id'] = cathedra

        if study_year or cathedra:
            cathedra_teacher_pks = TeacherPosition.objects.filter(**filter_d).values('profile')

            queryset = queryset.filter(pk__in=cathedra_teacher_pks)

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
            flow_uids = models.LessonStudent.objects.filter(group_id=group,
                                                            is_active=True).values('flow_uid')
            lessons = lessons.filter(flow_uid__in=flow_uids)

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

            is_teacher_empty = True
            resp['teacher'] = []
            resp['student'] = []
            resp['is_teacher'] = Role.objects.filter(profile=profile,
                                                     is_teacher=True).exists()
            resp['is_student'] = Role.objects.filter(profile=profile,
                                                     is_student=True).exists()

            teacher_lessons = lessons.filter(teachers__in=[profile])

            for day in work_week:
                teacher_day_lessons = teacher_lessons.filter(date=day).order_by('time__from_time')

                time_windows = models.TimeWindow.objects.filter(is_active=True).distinct('from_time', 'name').order_by('from_time')

                window_list = []
                for time_window in time_windows:
                    window_item = {
                        'id': time_window.uid,
                        'name': time_window.name,
                        'start': time_window.from_time.strftime('%H:%M'),
                        'end': time_window.to_time.strftime('%H:%M'),
                        'lesson': {},
                    }

                    try:
                        lesson = teacher_day_lessons.get(time=time_window)
                        window_item['lesson'] = self.serializer_class(lesson).data
                        is_teacher_empty = False
                    except models.Lesson.DoesNotExist:
                        pass

                    window_list.append(window_item)

                teacher_day = {
                    'date': day.strftime("%d.%m.%Y"),
                    'week_day': _(day.strftime('%A')),
                    'windows': window_list
                }
                resp['teacher'].append(teacher_day)

            resp['is_teacher_empty'] = is_teacher_empty

            my_group_pks = org_models.StudyPlan.objects.filter(
                student=profile,
                is_active=True,
            ).values('group')
            my_groups = org_models.Group.objects.filter(pk__in=my_group_pks)

            for my_group in my_groups:
                is_empty = True
                d = {
                    'group': my_group.name,
                    'days': []
                }

                my_group_flow_uids = models.LessonStudent.objects.filter(
                    Q(group=my_group,
                      student=profile,
                      is_active=True) |
                    Q(parent_group=my_group,
                      student=profile,  # Учитываю подгруппы
                      is_active=True),
                ).values('flow_uid')

                stud_lessons = lessons.filter(flow_uid__in=my_group_flow_uids)

                for day in work_week:
                    stud_day_lessons = stud_lessons.filter(date=day).order_by('time__from_time')

                    time_windows = models.TimeWindow.objects.filter(is_active=True).distinct('from_time', 'name').order_by('from_time')

                    window_list = []
                    for time_window in time_windows:
                        window_item = {
                            'id': time_window.uid,
                            'name': time_window.name,
                            'start': time_window.from_time.strftime('%H:%M'),
                            'end': time_window.to_time.strftime('%H:%M'),
                            'lesson': {},
                        }

                        try:
                            lesson = stud_day_lessons.get(time=time_window)
                            window_item['lesson'] = self.serializer_class(lesson).data
                            is_empty = False
                        except models.Lesson.DoesNotExist:
                            pass

                        window_list.append(window_item)

                    stud_day = {
                        'date': day.strftime("%d.%m.%Y"),
                        'week_day': _(day.strftime('%A')),
                        'windows': window_list,
                    }
                    d['days'].append(stud_day)
                d['is_empty'] = is_empty
                resp['student'].append(d)
        else:
            is_empty = True
            resp['days'] = []


            for day in work_week:
                day_lessons = lessons.filter(date=day).order_by('time__from_time')

                time_windows = models.TimeWindow.objects.filter(is_active=True).distinct('from_time', 'name').order_by('from_time')

                window_list = []
                for time_window in time_windows:
                    window_item = {
                        'id': time_window.uid,
                        'name': time_window.name,
                        'start': time_window.from_time.strftime('%H:%M'),
                        'end': time_window.to_time.strftime('%H:%M'),
                        'lesson': {},
                    }

                    try:
                        lesson = day_lessons.get(time=time_window)
                        window_item['lesson'] = self.serializer_class(lesson).data
                        is_empty = False
                    except models.Lesson.DoesNotExist:
                        pass

                    window_list.append(window_item)

                d = {
                    'date': day.strftime("%d.%m.%Y"),
                    'week_day': _(day.strftime('%A')),
                    'windows': window_list
                }
                resp['days'].append(d)
            resp['is_empty'] = is_empty


        resp_wrapper = {
            'next': CURRENT_API + '/schedules/?date={0}&next_week=1&group={1}&discipline={2}&teacher={3}&class_room={4}&my={5}'.format(
                monday,
                group,
                discipline,
                teacher,
                class_room,
                my_schedule,
            ),
            'prev': CURRENT_API + '/schedules/?date={0}&prev_week=1&group={1}&discipline={2}&teacher={3}&class_room={4}&my={5}'.format(
                monday,
                group,
                discipline,
                teacher,
                class_room,
                my_schedule,
            ),
            'last_date': CURRENT_API + '/schedules/?last_date={0}&next_week=1&group={1}&discipline={2}&teacher={3}&class_room={4}&my={5}'.format(
                monday,
                group,
                discipline,
                teacher,
                class_room,
                my_schedule,
            ),
            'first_date': CURRENT_API + '/schedules/?first_date={0}&next_week=1&group={1}&discipline={2}&teacher={3}&class_room={4}&my={5}'.format(
                monday,
                group,
                discipline,
                teacher,
                class_room,
                my_schedule,
            ),
            'results': resp

        }
        return Response(
            resp_wrapper,
            status=status.HTTP_200_OK
        )


class ElJournalListView(generics.ListAPIView):
    """
    Получить список ЭЖ для Преподавателя
    discipline, load_type, group, study_year
    """
    serializer_class = serializers.ElectronicJournalSerializer
    queryset = models.ElectronicJournal.objects.filter(is_active=True)

    def get_queryset(self):
        profile = self.request.user.profile
        discipline = self.request.query_params.get('discipline')
        load_type = self.request.query_params.get('load_type')
        group = self.request.query_params.get('group')
        study_year = self.request.query_params.get('study_year')

        flow_uids = models.LessonTeacher.objects.filter(teacher=profile).values('flow_uid')

        queryset = self.queryset.filter(flow_uid__in=flow_uids)

        if discipline:
            queryset = queryset.filter(discipline_id=discipline)
        if load_type:
            queryset = queryset.filter(load_type_id=load_type)
        if group:
            flow_uid_list = models.LessonStudent.objects.filter(
                Q(group_id=group) | Q(parent_group_id=group),
                is_active=True,
            ).values('flow_uid')
            queryset = queryset.filter(flow_uid__in=flow_uid_list)
        if study_year:
            queryset = queryset.filter(lessons__study_year_id=study_year)

        queryset = queryset.distinct()
        return queryset


class JournalInfoView(generics.RetrieveAPIView):  # TODO
    """
    Получить инфо о журнале для Препода
    id
    """
    permission_classes = (
        IsAuthenticated,
        permissions.ElJournalTeacherPermission,
    )
    serializer_class = serializers.ElectronicJournalDetailSerializer

    def get(self, request, *args, **kwargs):
        journal_id = request.query_params.get('id')
        try:
            journal = models.ElectronicJournal.objects.get(pk=journal_id)
        except models.ElectronicJournal.DoesNotExist:
            return Response(
                {
                    'message': 'not_found',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request,
                                      journal)
        serializer = self.serializer_class(journal)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class JournalDetailView(generics.RetrieveAPIView):
    """
    Получить журнал с оценками для Препода
    id, next_month, prev_month, date
    """
    permission_classes = (
        IsAuthenticated,
        permissions.ElJournalTeacherPermission,
    )

    def get(self, request, *args, **kwargs):
        journal_id = request.query_params.get('id')
        next_month = request.query_params.get('next_month')
        prev_month = request.query_params.get('prev_month')
        date_param = request.query_params.get('date')

        today = datetime.date.today()

        journal = models.ElectronicJournal.objects.get(pk=journal_id)
        self.check_object_permissions(request,
                                      journal)

        lessons = journal.lessons.filter(
            is_active=True,
        ).order_by('date', 'time__from_time')

        if len(lessons) == 0:
            return Response(
                {
                    "message": "no_lessons",
                },
                status=status.HTTP_404_NOT_FOUND
            )

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

        lesson_nums = []
        day_list = []
        student_list2 = []
        student_pks = models.LessonStudent.objects.filter(
            flow_uid=journal.flow_uid,
            is_active=True,
        ).values('student')
        students = Profile.objects.filter(pk__in=student_pks)

        for s in students:
            d = {
                'name': s.full_name,
                'short_name': s.name_initial,
                'id': s.uid,
            }
            student_list2.append(d)

        for day in days:
            day_d = {}
            day_lessons = lessons.filter(date=day['date'])
            lesson_num_in_day = len(day_lessons)
            lesson_nums.append(lesson_num_in_day)

            # if not day_lessons.exists():
            #     continue

            student_list = []
            times = []

            for student in students:
                stud_d = {}

                lesson_list = []
                times = []
                for lesson in day_lessons:
                    lesson_d = {}
                    time_d = {}

                    # edit_subject = True
                    # allow_mark = True
                    # if lesson.closed and not lesson.admin_allow:
                    #     """Занятие закрыто для оценивания и редактирования"""
                    #     edit_subject = False
                    #     allow_mark = False
                    #
                    # if today < lesson.date:
                    #     allow_mark = False

                    edit_subject, allow_mark = lesson_change_access(lesson)

                    reason = ''
                    try:
                        student_performance = models.StudentPerformance.objects.get(
                            student=student,
                            lesson=lesson,
                            is_active=True,
                        )
                        if student_performance.mark:
                            mark = serializers.MarkSerializer(student_performance.mark).data
                        else:
                            mark = {}

                        if student_performance.missed:
                            missed = 'H'
                            reason = student_performance.reason
                        else:
                            missed = ''
                    except models.StudentPerformance.DoesNotExist:
                        mark = {}
                        missed = ''

                    grading_system = serializers.GradingSystemSerializer(lesson.grading_system).data

                    lesson_d['lesson_id'] = lesson.uid
                    lesson_d['grading_system'] = grading_system
                    lesson_d['control'] = lesson.intermediate_control
                    lesson_d['mark'] = mark
                    lesson_d['missed'] = {
                        'missed': missed,
                        'reason': reason,
                    }
                    # lesson_d['reason'] = reason

                    lesson_d['allow_mark'] = allow_mark
                    lesson_list.append(lesson_d)

                    # time_d['date'] = day['date'].day
                    time_d['lesson_id'] = lesson.uid
                    time_d['start'] = lesson.time.from_time
                    time_d['edit_subject'] = edit_subject
                    time_d['grading_system'] = grading_system
                    time_d['subject_ru'] = lesson.subject_ru
                    time_d['subject_kk'] = lesson.subject_kk
                    time_d['subject_en'] = lesson.subject_en
                    times.append(time_d)

                stud_d['lessons'] = lesson_list
                stud_d['student'] = {
                    'id': student.uid,
                    'name': student.full_name,
                }
                student_list.append(stud_d)

            day_d['date'] = day['date'].day
            # day_d['lesson_num'] = lesson_num_in_day
            # times.sort(key=lambda item: item['start'])
            day_d['lessons'] = times

            day_d['students'] = student_list
            day_list.append(day_d)

        if len(lesson_nums) > 0:
            max_lesson_num = max(lesson_nums)
        else:
            max_lesson_num = 0

        resp = {
            'month': _(datetime.date(year=year, month=month, day=1).strftime("%B")),
            'year': year,
            'days': day_list,
            'students': student_list2,
            'max_lesson_num': max_lesson_num
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


class StudentPerformanceView(generics.RetrieveAPIView):
    """
    Получить инфо об успеваемости студента (1 клик по ячейке)
    student, lesson
    """
    permission_classes = (
        IsAuthenticated,
        permissions.LessonTeacherPermission,
    )

    def get(self, request, *args, **kwargs):
        student_id = request.query_params.get('student')
        lesson_id = request.query_params.get('lesson')

        student = Profile.objects.get(pk=student_id)
        lesson = models.Lesson.objects.get(pk=lesson_id)

        self.check_object_permissions(request,
                                      lesson)

        try:
            student_performance = models.StudentPerformance.objects.get(
                student=student,
                lesson=lesson,
                is_active=True,
            )
            if student_performance.mark:
                mark = student_performance.mark.value_number
            else:
                mark = ''

            if student_performance.missed:
                missed = 'H'
                reason = student_performance.reason
            else:
                missed = ''
                reason = ''
        except models.StudentPerformance.DoesNotExist:
            mark = ''
            missed = ''
            reason = ''

        resp = {
            'student': student.full_name,
            'date': lesson.date,
            'time': lesson.time.from_time,
            'mark': mark,
            'missed': missed,
            'reason': reason,
        }

        return Response(
            resp,
            status=status.HTTP_200_OK
        )


class AverageMarkView(generics.RetrieveAPIView):
    """
    Получить среднюю оценку студента по дисциплине
    student, discipline
    """
    permission_classes = (
        IsAuthenticated,
        permissions.LessonTeacherPermission,
    )

    def get(self, request, *args, **kwargs):
        student_id = request.query_params.get('student')
        discipline_id = request.query_params.get('discipline')

        student = Profile.objects.get(pk=student_id)
        discipline = org_models.Discipline.objects.get(pk=discipline_id)

        lessons = models.Lesson.objects.filter(discipline=discipline,
                                               is_active=True)
        mark_pks = models.StudentPerformance.objects.filter(
            student=student,
            lesson__in=lessons,
            is_active=True,
        ).values('mark')
        marks = models.Mark.objects.filter(pk__in=mark_pks)
        avg = marks.aggregate(avg=Avg('weight'))['avg']
        resp = {
            'avg': avg,
            'discipline': discipline.name,
            'student': student.name_initial,
        }
        return Response(
            resp,
            status=status.HTTP_200_OK
        )


class GetGradingSystemView(generics.RetrieveAPIView):
    """
    Получить систему оценивания занятия
    lesson
    """
    permission_classes = (
        IsAuthenticated,
        permissions.LessonTeacherPermission,
    )
    queryset = models.GradingSystem.objects.filter(is_active=True)
    serializer_class = serializers.GradingSystemSerializer

    def get(self, request, *args, **kwargs):
        lesson_id = request.query_params.get('lesson')
        lesson = models.Lesson.objects.get(pk=lesson_id)
        self.check_object_permissions(request,
                                      lesson)

        if lesson.grading_system:
            grading_system = lesson.grading_system
            serializer = self.serializer_class(grading_system)
            resp = serializer.data
        else:
            resp = {
                'message': 'no_grading_system',
            }

        return Response(
            resp,
            status=status.HTTP_200_OK,
        )


class EvaluateView(generics.CreateAPIView):
    """Поставить оценку или изменить оценку
    student, lesson, mark, missed, reason (Все параметры в теле POST запроса)
    """
    serializer_class = serializers.EvaluateSerializer
    permission_classes = (
        IsAuthenticated,
        permissions.LessonTeacherPermission,
    )

    def create(self, request, *args, **kwargs):
        lesson_id = request.data.get('lesson')
        lesson = models.Lesson.objects.get(pk=lesson_id)

        self.check_object_permissions(request,
                                      lesson)

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'message': 'ok',
            },
            status=status.HTTP_200_OK
        )


class GradingSystemListView(generics.ListAPIView):
    """Получить все системы оценивания"""
    queryset = models.GradingSystem.objects.filter(is_active=True)
    serializer_class = serializers.GradingSystemSerializer


class ChangeLessonView(generics.UpdateAPIView):
    """Изменить тему и систему оценивания занятия"""
    permission_classes = (
        IsAuthenticated,
        permissions.LessonTeacherPermission,
    )
    queryset = models.Lesson.objects.filter(is_active=True)
    serializer_class = serializers.LessonUpdateSerializer


class MarkListView(generics.ListAPIView):
    """Получить все оценки выбранной системы оценивания
    grading_system
    """
    queryset = models.Mark.objects.filter(is_active=True)
    serializer_class = serializers.MarkSerializer

    def get_queryset(self):
        grading_system = self.request.query_params.get('grading_system')
        queryset = self.queryset.filter(grading_system_id=grading_system).order_by('weight')

        return queryset


class ChooseControlView(generics.UpdateAPIView):
    """Выбор занятия как контрольное"""
    permission_classes = (
        IsAuthenticated,
        permissions.LessonTeacherPermission,
    )
    queryset = models.Lesson.objects.filter(is_active=True)
    serializer_class = serializers.ChooseControlSerializer


class LessonListView(generics.ListAPIView):
    """Список занятии для выбора контрольного
    discipline, load_type, flow_uid (Query Params)"""
    queryset = models.Lesson.objects.filter(is_active=True)
    serializer_class = serializers.LessonShortSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        discipline = self.request.query_params.get('discipline')
        load_type = self.request.query_params.get('load_type')
        flow_uid = self.request.query_params.get('flow_uid')

        today = datetime.date.today()

        queryset = self.queryset.filter(
            teachers__in=[profile],
            date__gt=today,
            is_active=True,
        ).order_by('date', 'time__from_time')

        if discipline:
            queryset = queryset.filter(discipline_id=discipline)
        if load_type:
            queryset = queryset.filter(load_type_id=load_type)
        if flow_uid:
            queryset = queryset.filter(flow_uid=flow_uid)

        return queryset
