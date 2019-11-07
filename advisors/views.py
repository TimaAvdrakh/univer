from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from organizations import models as org_models
from common.serializers import AcadPeriodSerializer
from common import models as common_models
from portal_users.serializers import EducationProgramSerializer, EducationProgramGroupSerializer, \
    StudyPlanSerializer, ProfileShortSerializer
from portal_users.models import Profile
from organizations.models import StudentDisciplineInfo
from portal.curr_settings import student_discipline_info_status, student_discipline_status
from django.db.models import Q, Count, Sum
from common.paginators import CustomPagination
from . import permissions as adv_permission
from rest_framework.permissions import IsAuthenticated
from . import models
from django.db.models import Q, Count, Max
from openpyxl import Workbook, load_workbook
from datetime import datetime
from django.shortcuts import HttpResponse
from uuid import uuid4
from portal_users.utils import get_current_study_year


class StudyPlansListView(generics.ListAPIView):
    """
    Получение учебных планов,
    study_year(!), study_form, faculty, cathedra, edu_prog_group, edu_prog, course, group, status
    """
    queryset = org_models.StudyPlan.objects.filter(is_active=True)
    serializer_class = serializers.StudyPlanSerializer

    def get_queryset(self):
        study_year = self.request.query_params.get('study_year')  # Дисциплина студента
        study_form = self.request.query_params.get('study_form')
        faculty = self.request.query_params.get('faculty')
        cathedra = self.request.query_params.get('cathedra')
        edu_prog_group = self.request.query_params.get('edu_prog_group')
        edu_prog = self.request.query_params.get('edu_prog')
        course = self.request.query_params.get('course')  # Дисциплина студента
        group = self.request.query_params.get('group')

        status_id = self.request.query_params.get('status')  # В Дисциплине студента
        # reg_period = self.request.query_params.get('reg_period')  # Дисциплина студента

        queryset = self.queryset.filter(advisor=self.request.user.profile)

        if status_id:
            status_obj = org_models.StudentDisciplineStatus.objects.get(number=status_id)

            study_plan_pks_from_sd = org_models.StudentDiscipline.objects.filter(
                study_year_id=study_year,
                status=status_obj,
            ).values('study_plan')

            queryset = queryset.filter(pk__in=study_plan_pks_from_sd)

        if study_form:
            queryset = queryset.filter(study_form_id=study_form)
        if faculty:
            queryset = queryset.filter(faculty_id=faculty)
        if cathedra:
            queryset = queryset.filter(cathedra_id=cathedra)
        if edu_prog:
            queryset = queryset.filter(education_program_id=edu_prog)
        if edu_prog_group:
            queryset = queryset.filter(education_program__group_id=edu_prog_group)
        if group:
            queryset = queryset.filter(group_id=group)
        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            queryset = queryset.filter(study_period__end__gt=study_year_obj.start)
        if course and study_year:
            study_plan_pks = org_models.StudyYearCourse.objects.filter(
                study_year_id=study_year,
                course=course
            ).values('study_plan')
            queryset = queryset.filter(pk__in=study_plan_pks)

        return queryset


class StudentDisciplineListView(generics.ListAPIView):
    """
    Получение дисциплин студента, query_params:
    study_plan(!), acad_period(!), status, short(!) (если значение 1, вернет только первые три записи)
    """
    queryset = org_models.StudentDiscipline.objects.filter(is_active=True)
    serializer_class = serializers.StudentDisciplineShortSerializer

    def list(self, request, *args, **kwargs):
        short = self.request.query_params.get('short')

        study_plan = self.request.query_params.get('study_plan')
        # study_year = self.request.query_params.get('study_year')
        acad_period = self.request.query_params.get('acad_period')
        status_id = self.request.query_params.get('status')
        # reg_period = self.request.query_params.get('reg_period')

        checks = models.AdvisorCheck.objects.filter(study_plan_id=study_plan,
                                                    acad_period_id=acad_period)

        if checks.exists():
            old_status = checks.latest('id').status
        else:
            old_status = 0

        queryset = self.queryset
        if study_plan:
            queryset = queryset.filter(study_plan_id=study_plan)
        if status_id:
            status_obj = org_models.StudentDisciplineStatus.objects.get(number=status_id)
            queryset = queryset.filter(status=status_obj)
        # if study_year:
        #     queryset = queryset.filter(study_year_id=study_year)
        if acad_period:
            queryset = queryset.filter(acad_period_id=acad_period)

        queryset = queryset.distinct('discipline')
        total_credit = sum(i.credit for i in queryset)

        is_more = len(queryset) > 3

        if int(short) == 1:
            queryset = queryset[:3]
        else:
            is_more = False

        serializer = self.serializer_class(instance=queryset,
                                           many=True)

        resp = {
            'total_credit': total_credit,
            'disciplines': serializer.data,
            'is_more': is_more,
            'old_status': old_status
        }

        return Response(
            resp,
            status=status.HTTP_200_OK
        )


class AcadPeriodListView(generics.ListAPIView):
    """Получить список акад периодов по курсу и периоду регистрации,
    study_year(!) reg_period(!), study_form, faculty, cathedra, edu_prog_group, edu_prog, course, group, status
    """

    queryset = org_models.AcadPeriod.objects.filter(is_active=True)
    serializer_class = AcadPeriodSerializer

    def get_queryset(self):
        reg_period = self.request.query_params.get('reg_period')
        study_year = self.request.query_params.get('study_year')

        course = self.request.query_params.get('course')
        study_form = self.request.query_params.get('study_form')
        faculty = self.request.query_params.get('faculty')
        cathedra = self.request.query_params.get('cathedra')
        edu_prog_group = self.request.query_params.get('edu_prog_group')
        edu_prog = self.request.query_params.get('edu_prog')
        group = self.request.query_params.get('group')
        status_id = self.request.query_params.get('status')

        profile = self.request.user.profile

        if course:
            acad_period_pks = common_models.CourseAcadPeriodPermission.objects.filter(
                registration_period_id=reg_period,
                course=course
            ).values('acad_period')
        else:
            acad_period_pks = common_models.CourseAcadPeriodPermission.objects.filter(
                registration_period_id=reg_period,
            ).values('acad_period')

        acad_periods = self.queryset.filter(pk__in=acad_period_pks)

        sd = org_models.StudentDiscipline.objects.filter(
            study_plan__advisor=profile,
            study_year_id=study_year,
        )

        if study_form:
            sd = sd.filter(study_plan__study_form_id=study_form)
        if faculty:
            sd = sd.filter(study_plan__faculty_id=faculty)
        if cathedra:
            sd = sd.filter(study_plan__cathedra_id=cathedra)
        if edu_prog_group:
            sd = sd.filter(study_plan__education_program__group_id=edu_prog_group)
        if edu_prog:
            sd = sd.filter(study_plan__education_program_id=edu_prog)
        if group:
            sd = sd.filter(study_plan__group_id=group)
        if status_id:
            status_obj = org_models.StudentDisciplineStatus.objects.get(number=status_id)
            sd = sd.filter(status=status_obj)

        acad_period_pks_from_sd = sd.values('acad_period')

        acad_periods = acad_periods.filter(pk__in=acad_period_pks_from_sd)

        return acad_periods


class FacultyListView(generics.ListAPIView):
    """Получить список факультетов доступных для эдвайзеру, query_params: study_year(!), study_form"""
    queryset = org_models.Faculty.objects.filter(is_active=True)
    serializer_class = serializers.FacultySerializer

    def get_queryset(self):
        profile = self.request.user.profile

        study_year = self.request.query_params.get('study_year')
        study_form = self.request.query_params.get('study_form')
        study_plans = org_models.StudyPlan.objects.filter(advisor=profile)

        if study_form:
            study_plans = study_plans.filter(study_form_id=study_form)
        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plans = study_plans.filter(study_period__end__gt=study_year_obj.start)

        faculty_pks = study_plans.values('faculty')

        queryset = self.queryset.filter(pk__in=faculty_pks)
        return queryset


class CathedraListView(generics.ListAPIView):
    """Получить список кафедр доступных для эдвайзеру, query_params: study_year, study_form, faculty"""

    queryset = org_models.Cathedra.objects.filter(is_active=True)
    serializer_class = serializers.CathedraSerializer

    def get_queryset(self):
        profile = self.request.user.profile

        study_year = self.request.query_params.get('study_year')
        study_form = self.request.query_params.get('study_form')
        faculty = self.request.query_params.get('faculty')

        study_plans = org_models.StudyPlan.objects.filter(advisor=profile)

        if study_form:
            study_plans = study_plans.filter(study_form_id=study_form)
        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plans = study_plans.filter(study_period__end__gt=study_year_obj.start)

        cathedra_pks = study_plans.values('cathedra')
        queryset = self.queryset.filter(pk__in=cathedra_pks)

        if faculty:
            queryset = queryset.filter(faculty_id=faculty)

        return queryset


class EducationProgramGroupListView(generics.ListAPIView):
    """Получить список групп образовательных программ.
    study_year, study_form, faculty, cathedra, speciality(для 2 стр (Утвержденные дисциплины))"""

    queryset = org_models.EducationProgramGroup.objects.filter(is_active=True)
    serializer_class = EducationProgramGroupSerializer

    def get_queryset(self):
        profile = self.request.user.profile

        study_year = self.request.query_params.get('study_year')
        study_form = self.request.query_params.get('study_form')
        cathedra = self.request.query_params.get('cathedra')
        faculty = self.request.query_params.get('faculty')
        speciality = self.request.query_params.get('speciality')  # Для утвержденных дисциплин

        study_plans = org_models.StudyPlan.objects.filter(advisor=profile)

        if study_form:
            study_plans = study_plans.filter(study_form_id=study_form)
        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plans = study_plans.filter(study_period__end__gt=study_year_obj.start)
        if faculty:
            study_plans = study_plans.filter(faculty_id=faculty)
        if cathedra:
            study_plans = study_plans.filter(cathedra_id=cathedra)
        if speciality:  # Для утвержденных дисциплин
            study_plans = study_plans.filter(speciality_id=speciality)

        education_program_pks = study_plans.values('education_program')
        queryset = self.queryset.filter(educationprogram__in=education_program_pks)

        return queryset


class EducationProgramListView(generics.ListAPIView):
    """Получить список образовательных программ,
    edu_prog_group=<uid edu_prog_group>, study_year"""

    queryset = org_models.EducationProgram.objects.filter(is_active=True)
    serializer_class = EducationProgramSerializer

    def get_queryset(self):
        profile = self.request.user.profile

        study_year = self.request.query_params.get('study_year')
        study_form = self.request.query_params.get('study_form')
        edu_prog_group = self.request.query_params.get('edu_prog_group')
        cathedra = self.request.query_params.get('cathedra')
        faculty = self.request.query_params.get('faculty')

        study_plans = org_models.StudyPlan.objects.filter(advisor=profile)

        if study_form:
            study_plans = study_plans.filter(study_form_id=study_form)
        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plans = study_plans.filter(study_period__end__gt=study_year_obj.start)
        if faculty:
            study_plans = study_plans.filter(faculty_id=faculty)
        if cathedra:
            study_plans = study_plans.filter(cathedra_id=cathedra)

        education_program_pks = study_plans.values('education_program')
        queryset = self.queryset.filter(pk__in=education_program_pks)

        if edu_prog_group:
            queryset = queryset.filter(group_id=edu_prog_group)
        return queryset


class GroupListView(generics.ListAPIView):
    """Получить список групп,
    study_year, study_form, faculty, cathedra, edu_prog, course"""

    queryset = org_models.Group.objects.filter(is_active=True)
    serializer_class = serializers.GroupShortSerializer

    def get_queryset(self):
        profile = self.request.user.profile

        study_year = self.request.query_params.get('study_year')
        study_form = self.request.query_params.get('study_form')
        cathedra = self.request.query_params.get('cathedra')
        faculty = self.request.query_params.get('faculty')

        edu_prog = self.request.query_params.get('edu_prog')
        course = self.request.query_params.get('course')
        speciality = self.request.query_params.get('speciality')  # Для утвержденных дисциплин

        study_plans = org_models.StudyPlan.objects.filter(advisor=profile)

        if study_form:
            study_plans = study_plans.filter(study_form_id=study_form)
        if edu_prog:
            study_plans = study_plans.filter(education_program_id=edu_prog)

        if course and study_year:
            study_plan_pks = org_models.StudyYearCourse.objects.filter(
                study_year_id=study_year,
                course=course
            ).values('study_plan')

            study_plans = study_plans.filter(pk__in=study_plan_pks)

        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plans = study_plans.filter(study_period__end__gt=study_year_obj.start)
        if faculty:
            study_plans = study_plans.filter(faculty_id=faculty)
        if cathedra:
            study_plans = study_plans.filter(cathedra_id=cathedra)

        if speciality:  # Для утвержденных дисциплин
            study_plans = study_plans.filter(speciality_id=speciality)

        group_pks = study_plans.values('group')
        queryset = self.queryset.filter(pk__in=group_pks)

        return queryset


class CheckStudentChoices(generics.CreateAPIView):
    """Утвердить или отклонить заявки студента. Статус: 4 - утврежден, 3 - отклонен"""
    serializer_class = serializers.CheckStudentBidsSerializer
    permission_classes = (
        IsAuthenticated,
        adv_permission.StudyPlanAdvisorPermission
    )

    def create(self, request, *args, **kwargs):
        try:
            sp = org_models.StudyPlan.objects.get(pk=request.data['study_plan'])
        except org_models.StudyPlan.DoesNotExist:
            return Response(
                {
                    "message": "not_found",
                },
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request,
                                      sp)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'message': 'ok'
            },
            status=status.HTTP_200_OK
        )


class FilteredStudentsListView(generics.ListAPIView):
    """Фильтровать студентов для селекта (Эдвайзер)
        study_year(!), edu_prog(!), faculty, speciality, group"""
    serializer_class = ProfileShortSerializer

    def get_queryset(self):
        request = self.request

        study_year = request.query_params.get('study_year')
        faculty = request.query_params.get('faculty')
        speciality = request.query_params.get('speciality')
        edu_prog = request.query_params.get('edu_prog')
        group = request.query_params.get('group')

        study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)

        study_plans = org_models.StudyPlan.objects.filter(
            study_period__end__gt=study_year_obj.start,
            is_active=True,
        )

        if edu_prog:
            study_plans = study_plans.filter(education_program_id=edu_prog)

        if faculty:
            study_plans = study_plans.filter(faculty_id=faculty)

        if speciality:
            study_plans = study_plans.filter(speciality_id=speciality)

        if group:
            study_plans = study_plans.filter(group_id=group)

        student_pks = study_plans.values('student')
        students = Profile.objects.filter(pk__in=student_pks)

        return students


class SpecialityListView(generics.ListAPIView):
    """Получить список специальностей доступных эдвайзеру,
    study_year(!), faculty"""

    queryset = org_models.Speciality.objects.filter(is_active=True)
    serializer_class = serializers.SpecialitySerializer

    def get_queryset(self):
        profile = self.request.user.profile

        study_year = self.request.query_params.get('study_year')
        faculty = self.request.query_params.get('faculty')

        study_plans = org_models.StudyPlan.objects.filter(advisor=profile)

        if faculty:
            study_plans = study_plans.filter(faculty_id=faculty)

        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plans = study_plans.filter(study_period__end__gt=study_year_obj.start)

        speciality_pks = study_plans.values('speciality')
        queryset = self.queryset.filter(pk__in=speciality_pks)

        return queryset


class GetStudyPlanView(generics.RetrieveAPIView):
    """Получить учебный план студента для ИУПы обучающихся (2 стр, Утвержденные)
        study_year(!), edu_prog(!), student(!), faculty, speciality, group
    """
    serializer_class = serializers.StudyPlanDetailSerializer

    def get(self, request, *args, **kwargs):
        study_year = request.query_params.get('study_year')
        faculty = request.query_params.get('faculty')
        speciality = request.query_params.get('speciality')
        edu_prog = request.query_params.get('edu_prog')
        group = request.query_params.get('group')
        student = request.query_params.get('student')

        filters = {}

        if faculty:
            filters['faculty_id'] = faculty

        if speciality:
            filters['speciality_id'] = speciality

        if group:
            filters['group_id'] = group

        try:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plan = org_models.StudyPlan.objects.get(
                study_period__end__gt=study_year_obj.start,
                education_program_id=edu_prog,
                student_id=student,
                is_active=True,
                **filters,
            )
        except org_models.StudyPlan.DoesNotExist:
            return Response(
                {
                    'message': 0  # Учебный план не найден
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(instance=study_plan,
                                           context={'study_year_obj': study_year_obj})
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ConfirmedStudentDisciplineListView(generics.ListAPIView):
    """Получить все утвержденные дисциплины выбранного учебного плана
        study_plan(!), study_year(!)"""

    serializer_class = serializers.ConfirmedStudentDisciplineShortSerializer

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get('study_plan')
        study_year = request.query_params.get('study_year')

        # study_plan = org_models.StudyPlan.objects.get(pk=study_plan_id,
        #                                               is_active=True)
        # study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
        # course = study_plan.get_course(study_year_obj)

        acad_periods = org_models.StudentDiscipline.objects.filter(
            study_year_id=study_year,
            study_plan_id=study_plan_id
        ).distinct('acad_period').values('acad_period')

        resp = []

        for acad_period in acad_periods:
            acad_period_id = acad_period['acad_period']
            acad_period_obj = org_models.AcadPeriod.objects.get(pk=acad_period_id)

            if StudentDisciplineInfo.objects.filter(
                    study_plan_id=study_plan_id,
                    acad_period_id=acad_period_id,
                    status_id=student_discipline_info_status['confirmed'],
            ).exists():
                student_disciplines = org_models.StudentDiscipline.objects.filter(
                    study_year_id=study_year,
                    study_plan_id=study_plan_id,
                    acad_period_id=acad_period_id,
                ).distinct('discipline')

                serializer = self.serializer_class(student_disciplines,
                                                   many=True)
                item = {
                    'acad_period': acad_period_obj.repr_name,
                    'disciplines': serializer.data,
                    # 'course': course
                }
                resp.append(item)

        return Response(
            resp,
            status=status.HTTP_200_OK
        )


class RegisterResultView(generics.ListAPIView):
    """Результат регистрации
        study_year(!), reg_period(!), acad_period, faculty, speciality, edu_prog, course, group
    """
    serializer_class = serializers.StudentDisciplineSerializer
    queryset = org_models.StudentDiscipline.objects.filter(is_active=True)
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        study_year = request.query_params.get('study_year')
        reg_period = request.query_params.get(
            'reg_period')  # TODO если не указан акад период, брать акад периоды из периода регистрации
        acad_period = self.request.query_params.get('acad_period')
        faculty = request.query_params.get('faculty')
        speciality = request.query_params.get('speciality')
        edu_prog = request.query_params.get('edu_prog')
        course = request.query_params.get('course')
        group = request.query_params.get('group')

        queryset = self.queryset
        queryset = queryset.filter(status_id=student_discipline_status['confirmed'])

        if acad_period:
            queryset = queryset.filter(acad_period_id=acad_period)
        if faculty:
            queryset = queryset.filter(study_plan__faculty_id=faculty)
        if speciality:
            queryset = queryset.filter(study_plan__speciality_id=speciality)
        if edu_prog:
            queryset = queryset.filter(study_plan__education_program_id=edu_prog)
        if group:
            queryset = queryset.filter(study_plan__group_id=group)
        if study_year:
            queryset = queryset.filter(study_year_id=study_year)

        if course and study_year:
            study_plan_pks = org_models.StudyYearCourse.objects.filter(
                study_year_id=study_year,
                course=course
            ).values('study_plan')
            queryset = queryset.filter(study_plan__in=study_plan_pks)

        distincted_queryset = queryset.distinct('discipline', 'load_type', 'hours', 'language', 'teacher')

        student_discipline_list = []
        for item in distincted_queryset:
            student_count = queryset.filter(
                discipline=item.discipline,
                load_type=item.load_type,
                language=item.language,
                teacher=item.teacher,
                hours=item.hours,
            ).distinct('student').count()
            d = {
                'discipline': item.discipline,
                'load_type': item.load_type,
                'hours': item.hours,
                'language': item.language,
                'teacher': item.teacher,
                'student_count': student_count
            }
            student_discipline_list.append(d)

        page = self.paginate_queryset(student_discipline_list)
        if page is not None:
            serializer = self.serializer_class(page,
                                               many=True)
            return self.get_paginated_response(serializer.data)

        # serializer = self.serializer_class(student_discipline_list,
        #                                    many=True)
        # return Response(
        #     serializer.data,
        #     status=status.HTTP_200_OK,
        # )


class RegisterStatisticsView(generics.ListAPIView):
    """Статистика регистрации
    study_year(!), reg_period(!), acad_period, faculty, speciality, edu_prog, course, group
    """
    serializer_class = serializers.RegisterStatisticsSerializer
    queryset = org_models.StudentDiscipline.objects.filter(is_active=True)
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        study_year = request.query_params.get('study_year')
        reg_period = request.query_params.get(
            'reg_period')  # TODO если не указан акад период, брать акад периоды из периода регистрации
        acad_period = request.query_params.get('acad_period')
        faculty = request.query_params.get('faculty')
        speciality = request.query_params.get('speciality')
        edu_prog = request.query_params.get('edu_prog')
        course = request.query_params.get('course')
        group = request.query_params.get('group')

        queryset = self.queryset
        queryset = queryset.filter(status_id=student_discipline_status['not_chosen'])

        if acad_period:
            queryset = queryset.filter(acad_period_id=acad_period)
        if faculty:
            queryset = queryset.filter(study_plan__faculty_id=faculty)
        if speciality:
            queryset = queryset.filter(study_plan__speciality_id=speciality)
        if edu_prog:
            queryset = queryset.filter(study_plan__education_program_id=edu_prog)
        if group:
            queryset = queryset.filter(study_plan__group_id=group)
        if study_year:
            queryset = queryset.filter(study_year_id=study_year)

        if course and study_year:
            study_plan_pks = org_models.StudyYearCourse.objects.filter(
                study_year_id=study_year,
                course=course
            ).values('study_plan')
            queryset = queryset.filter(study_plan__in=study_plan_pks)

        distincted_queryset = queryset.distinct('discipline', 'study_plan__group')

        student_discipline_list = []
        for student_discipline in distincted_queryset:
            group_student_count = org_models.StudyPlan.objects.filter(
                group=student_discipline.study_plan.group,
                is_active=True,
            ).distinct('student').count()

            not_chosen_student_count = queryset.filter(
                study_plan__group=student_discipline.study_plan.group,
                discipline=student_discipline.discipline
            ).distinct('student').count()

            d = {
                'faculty': student_discipline.study_plan.faculty.name,
                'cathedra': student_discipline.study_plan.cathedra.name,
                'speciality': student_discipline.study_plan.speciality.name,
                'group': student_discipline.study_plan.group.name,
                'student_count': group_student_count,
                'discipline': student_discipline.discipline.name,
                'not_chosen_student_count': not_chosen_student_count,
                'percent_of_non_chosen_student': (not_chosen_student_count / group_student_count) * 100,
            }
            student_discipline_list.append(d)

        page = self.paginate_queryset(student_discipline_list)
        if page is not None:
            serializer = self.serializer_class(page,
                                               many=True)
            return self.get_paginated_response(serializer.data)

        # return Response(
        #     serializer.data,
        #     status=status.HTTP_200_OK,
        # )


class NotRegisteredStudentListView(generics.ListAPIView):
    """Списке незарегистрированных
    study_year(!), reg_period(!), acad_period, faculty, speciality, edu_prog, course, group
    """
    pagination_class = CustomPagination
    queryset = org_models.StudentDiscipline.objects.filter(
        is_active=True
    ).distinct('student')
    serializer_class = serializers.NotRegisteredStudentSerializer

    def get_queryset(self):
        study_year = self.request.query_params.get('study_year')
        reg_period = self.request.query_params.get(
            'reg_period')  # TODO если не указан акад период, брать акад периоды из периода регистрации
        acad_period = self.request.query_params.get('acad_period')
        faculty = self.request.query_params.get('faculty')
        speciality = self.request.query_params.get('speciality')
        edu_prog = self.request.query_params.get('edu_prog')
        course = self.request.query_params.get('course')
        group = self.request.query_params.get('group')

        queryset = self.queryset
        queryset = queryset.filter(status_id=student_discipline_status['not_chosen'])

        if acad_period:
            queryset = queryset.filter(acad_period_id=acad_period)
        if faculty:
            queryset = queryset.filter(study_plan__faculty_id=faculty)
        if speciality:
            queryset = queryset.filter(study_plan__speciality_id=speciality)
        if edu_prog:
            queryset = queryset.filter(study_plan__education_program_id=edu_prog)
        if group:
            queryset = queryset.filter(study_plan__group_id=group)
        if study_year:
            queryset = queryset.filter(study_year_id=study_year)

        if course and study_year:
            study_plan_pks = org_models.StudyYearCourse.objects.filter(
                study_year_id=study_year,
                course=course
            ).values('study_plan')
            queryset = queryset.filter(study_plan__in=study_plan_pks)

        return queryset


class GenerateIupBidExcelView(generics.RetrieveAPIView):
    """Генерировать Excel для Заявки на ИУПы
        study_year(!), study_form, faculty, cathedra, edu_prog_group, edu_prog,
        course, group, acad_periods
    """

    def get(self, request, *args, **kwargs):
        study_year = request.query_params.get('study_year')  # Дисциплина студента
        study_form = request.query_params.get('study_form')
        faculty = request.query_params.get('faculty')
        cathedra = request.query_params.get('cathedra')
        edu_prog_group = request.query_params.get('edu_prog_group')
        edu_prog = request.query_params.get('edu_prog')
        course = request.query_params.get('course')  # Дисциплина студента
        group = request.query_params.get('group')
        reg_period = self.request.query_params.get('reg_period')
        status_id = self.request.query_params.get('status')  # В Дисциплине студента
        acad_periods = self.request.query_params.get('acad_periods')

        wb = load_workbook('advisors/excel/template.xlsx')
        ws = wb.active

        queryset = org_models.StudyPlan.objects.filter(is_active=True). \
            filter(advisor=self.request.user.profile)

        if reg_period:
            reg_period_obj = common_models.RegistrationPeriod.objects.get(pk=reg_period)
            ws['B4'] = reg_period_obj.name
        if course:
            ws['B5'] = course

        if status_id:
            status_obj = org_models.StudentDisciplineStatus.objects.get(number=status_id)
            ws['B6'] = status_obj.name
        else:
            ws['B6'] = 'Все'

        if study_form:
            study_form_obj = org_models.StudyForm.objects.get(pk=study_form)
            ws['B7'] = study_form_obj.name
            queryset = queryset.filter(study_form_id=study_form)
        else:
            ws['B7'] = 'Все'

        if faculty:
            faculty_obj = org_models.Faculty.objects.get(pk=faculty)
            queryset = queryset.filter(faculty_id=faculty)
            ws['B8'] = faculty_obj.name
        else:
            ws['B8'] = 'Все'

        if cathedra:
            cathedra_obj = org_models.Cathedra.objects.get(pk=cathedra)
            queryset = queryset.filter(cathedra_id=cathedra)
            ws['B9'] = cathedra_obj.name
        else:
            ws['B9'] = 'Все'

        if edu_prog_group:
            queryset = queryset.filter(education_program__group_id=edu_prog_group)
            edu_prog_group_obj = org_models.EducationProgramGroup.objects.get(pk=edu_prog_group)
            ws['B10'] = edu_prog_group_obj.name
        else:
            ws['B10'] = 'Все'

        if edu_prog:
            queryset = queryset.filter(education_program_id=edu_prog)
            edu_prog_obj = org_models.EducationProgram.objects.get(pk=edu_prog)
            ws['B11'] = edu_prog_obj.name
        else:
            ws['B11'] = 'Все'

        if group:
            queryset = queryset.filter(group_id=group)
            group_obj = org_models.Group.objects.get(pk=group)
            ws['B12'] = group_obj.name
        else:
            ws['B12'] = 'Все'

        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            queryset = queryset.filter(study_period__end__gt=study_year_obj.start)
            ws['B3'] = '{} - {}'.format(study_year_obj.start,
                                        study_year_obj.end)

        if course and study_year:
            study_plan_pks = org_models.StudyYearCourse.objects.filter(
                study_year_id=study_year,
                course=course
            ).values('study_plan')
            queryset = queryset.filter(pk__in=study_plan_pks)

        now = datetime.now()
        ws['B13'] = now.strftime("%d:%m:%Y, %H:%M:%S")

        for i, study_plan in enumerate(queryset):
            row_num = str(15 + i)

            a = 'A' + row_num
            ws[a] = i + 1

            b = 'B' + row_num
            ws[b] = study_plan.education_program.group.code

            c = 'C' + row_num
            ws[c] = study_plan.education_program.name

            d = 'D' + row_num
            ws[d] = study_plan.group.name

            e = 'E' + row_num
            ws[e] = study_plan.student.full_name

            columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                       'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']

            current_col_num = 5
            sum_credit = 0
            old_status = 0
            mark_text = ''

            if acad_periods and len(acad_periods) > 0:
                acad_period_list = acad_periods.split(',')

                for i, acad_period in enumerate(acad_period_list):
                    acad_period_obj = org_models.AcadPeriod.objects.get(pk=acad_period)
                    head = '{} триместр Перечень дисциплин, ' \
                           'на которые проведена  регистрация ' \
                           'с указанием кредитов'.format(acad_period_obj.number)

                    student_disciplines = org_models.StudentDiscipline.objects.filter(
                        is_active=True,
                        study_plan=study_plan,
                        acad_period_id=acad_period,
                    ).distinct('discipline')

                    student_discipline_list = list(student_disciplines)
                    credit_list = [i.credit for i in student_discipline_list]
                    total_credit = sum(credit_list)
                    sum_credit += total_credit

                    text = 'Кредиты: {}\n'.format(total_credit)

                    for stud_discipline in student_disciplines:
                        text += '{} ({})\n'.format(stud_discipline.discipline.name,
                                                   stud_discipline.credit)

                    head_cell = columns[current_col_num] + '14'
                    ws[head_cell] = head

                    text_cell = columns[current_col_num] + row_num
                    ws[text_cell] = text

                    current_col_num += 1

                    checks = models.AdvisorCheck.objects.filter(
                        study_plan=study_plan,
                        acad_period_id=acad_period,
                    )
                    if checks.exists():
                        old_status = checks.latest('id').status
                    else:
                        old_status = 0

                    if old_status == 3:
                        mark = '{} - Отклонено\n'.format(acad_period_obj.repr_name)
                    elif old_status == 4:
                        mark = '{} - Утверждено\n'.format(acad_period_obj.repr_name)
                    elif old_status == 5:
                        mark = '{} - Изменено\n'.format(acad_period_obj.repr_name)
                    else:
                        mark = '{} - Не определено\n'.format(acad_period_obj.repr_name)

                    mark_text += mark

            gos_attestation_label = columns[current_col_num] + '14'
            ws[gos_attestation_label] = 'Государственная аттестация'
            gos_attestation = columns[current_col_num] + row_num
            ws[gos_attestation] = 'не выбрана'

            current_col_num += 1
            sum_credit_label = columns[current_col_num] + '14'
            ws[sum_credit_label] = 'Общее количество кредитов'
            sum_credit_cell = columns[current_col_num] + row_num
            ws[sum_credit_cell] = sum_credit

            current_col_num += 1
            advisor_mark_label = columns[current_col_num] + '14'
            ws[advisor_mark_label] = 'Отметка эдвайзера'
            mark_cell = columns[current_col_num] + row_num
            ws[mark_cell] = mark_text

        file_name = 'temp_files/zayavki{}.xlsx'.format(str(uuid4()))
        wb.save(file_name)

        with open(file_name, 'rb') as f:
            response = HttpResponse(f, content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="zayavki' + str(uuid4()) + '.xls"'
            return response

        # return Response(
        #     {
        #         'message': 'ok'
        #     },
        #     status=status.HTTP_200_OK
        # )


class GenerateIupExcelView(generics.RetrieveAPIView):
    """
    study_year(!), edu_prog(!), student(!), faculty, speciality, group,
    """

    def get(self, request, *args, **kwargs):
        study_year = request.query_params.get('study_year')
        edu_prog = request.query_params.get('edu_prog')
        student = request.query_params.get('student')

        faculty = request.query_params.get('faculty')
        speciality = request.query_params.get('speciality')
        group = request.query_params.get('group')

        wb = load_workbook('advisors/excel/template2.xlsx')
        ws = wb.active

        filters = {}

        if faculty:
            filters['faculty_id'] = faculty

        if speciality:
            filters['speciality_id'] = speciality

        if group:
            filters['group_id'] = group

        try:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plan = org_models.StudyPlan.objects.get(
                study_period__end__gt=study_year_obj.start,
                education_program_id=edu_prog,
                student_id=student,
                is_active=True,
                **filters,
            )
        except org_models.StudyPlan.DoesNotExist:
            return Response(
                {
                    'message': 0  # Учебный план не найден
                },
                status=status.HTTP_404_NOT_FOUND
            )

        student_name_cell = 'D17'
        ws[student_name_cell] = study_plan.student.full_name

        acad_degree_cell = 'D19'
        ws[acad_degree_cell] = study_plan.preparation_level.name

        speciality_cell = 'D20'
        ws[speciality_cell] = '{} ({})'.format(study_plan.speciality.name,
                                               study_plan.speciality.code)

        study_form_cell = 'D22'
        max_course = \
            org_models.StudyYearCourse.objects.filter(study_plan=study_plan).aggregate(max_course=Max('course'))[
                'max_course']
        ws[study_form_cell] = '{}, {} года'.format(study_plan.study_form.name, max_course)

        current_course_cell = 'D24'
        ws[current_course_cell] = study_plan.current_course

        lang_cell = 'D25'
        ws[lang_cell] = study_plan.group.language.name

        current_study_year_cell = 'D26'
        study_year_dict = get_current_study_year()
        ws[current_study_year_cell] = '{}-{}'.format(study_year_dict['start'],
                                                     study_year_dict['end'])

        course = study_plan.get_course(study_year_obj)
        ws['D30'] = '{} Курс обучения  {} учебный год'.format(course,
                                                              str(study_year_obj))

        acad_periods = org_models.StudentDiscipline.objects.filter(
            study_year_id=study_year,
            study_plan=study_plan,
        ).distinct('acad_period').values('acad_period')

        row_num = 31
        sd_num = 1
        total_credit_in_course = 0

        for acad_period in acad_periods:
            acad_period_id = acad_period['acad_period']
            acad_period_obj = org_models.AcadPeriod.objects.get(pk=acad_period_id)

            if StudentDisciplineInfo.objects.filter(
                    study_plan=study_plan,
                    acad_period_id=acad_period_id,
                    status_id=student_discipline_info_status['confirmed'],
            ).exists():
                student_disciplines = org_models.StudentDiscipline.objects.filter(
                    study_year_id=study_year,
                    study_plan=study_plan,
                    acad_period_id=acad_period_id,
                ).distinct('discipline')

                ws['D' + str(row_num)] = acad_period_obj.repr_name
                row_num += 1

                total_credit_in_acad_period = 0

                for sd in student_disciplines:
                    num_cell = 'A' + str(row_num)
                    ws[num_cell] = sd_num

                    component_cell = 'B' + str(row_num)
                    ws[component_cell] = sd.component.short_name or sd.cycle.short_name

                    discipline_code_cell = 'C' + str(row_num)
                    ws[discipline_code_cell] = sd.discipline_code

                    discipline_name_cell = 'D' + str(row_num)
                    ws[discipline_name_cell] = sd.discipline.name

                    credit_cell = 'E' + str(row_num)
                    ws[credit_cell] = sd.credit

                    total_credit_in_acad_period += sd.credit

                    row_num += 1
                    sd_num += 1

                total_credit_in_course += total_credit_in_acad_period
                ws['D' + str(row_num)] = 'Общее количество кредитов: {}'.format(total_credit_in_acad_period)
                row_num += 1

        ws['D' + str(row_num)] = 'Общее количество кредитов за курс: {}'.format(total_credit_in_course)
        row_num += 2
        ws['A' + str(row_num)] = 'Регистратор'

        row_num += 2
        ws['A' + str(row_num)] = 'Эдвайзер'

        row_num += 2
        ws['A' + str(row_num)] = 'Обучающийся:'

        file_name = 'temp_files/iupi{}.xlsx'.format(str(uuid4()))
        wb.save(file_name)

        with open(file_name, 'rb') as f:
            response = HttpResponse(f, content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="zayavki' + str(uuid4()) + '.xls"'
            return response

        # return Response(
        #     {
        #         'message': 'ok'
        #     },
        #     status=status.HTTP_200_OK
        # )
