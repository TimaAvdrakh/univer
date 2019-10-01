from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from organizations import models as org_models
from common.serializers import AcadPeriodSerializer
from common import models as common_models
from portal_users.serializers import EducationProgramSerializer, EducationProgramGroupSerializer


class RegistrationBidListView(generics.ListAPIView):
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

        # status = self.request.query_params.get('status')  # В Дисциплине студента
        # reg_period = self.request.query_params.get('reg_period')  # Дисциплина студента

        queryset = self.queryset

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
    query_params: study_plan, acad_period, status, short (если значение 1, вернет только первые три записи)
    """
    queryset = org_models.StudentDiscipline.objects.filter(is_active=True)
    serializer_class = serializers.StudentDisciplineShortSerializer

    def get_queryset(self):
        short = self.request.query_params.get('short')

        study_plan = self.request.query_params.get('study_plan')
        # study_year = self.request.query_params.get('study_year')
        acad_period = self.request.query_params.get('acad_period')
        status = self.request.query_params.get('status')
        # reg_period = self.request.query_params.get('reg_period')

        queryset = self.queryset
        if study_plan:
            queryset = queryset.filter(study_plan_id=study_plan)
        if status:
            status_obj = org_models.StudentDisciplineStatus.objects.get(number=status)
            queryset = queryset.filter(status=status_obj)
        # if study_year:
        #     queryset = queryset.filter(study_year_id=study_year)
        if acad_period:
            queryset = queryset.filter(acad_period_id=acad_period)

        if int(short) == 1:
            queryset = queryset[:3]

        return queryset


class AcadPeriodListView(generics.ListAPIView):
    """Получить список акад периодов по курсу и периоду регистрации"""

    queryset = org_models.AcadPeriod.objects.filter(is_active=True)
    serializer_class = AcadPeriodSerializer

    def get_queryset(self):
        reg_period = self.request.query_params.get('reg_period')
        course = self.request.query_params.get('course')

        acad_period_pks = common_models.CourseAcadPeriodPermission.objects.filter(
            registration_period_id=reg_period,
            course=course
        ).values('acad_period')
        acad_periods = self.queryset.filter(pk__in=acad_period_pks)

        return acad_periods


class FacultyListView(generics.ListAPIView):
    """Получить список факультетов доступных для эдвайзеру"""
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
    """Получить список кафедр доступных для эдвайзеру
    query_params:  faculty=<uid faculty> необязательно"""

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
    """Получить список групп образовательных программ"""

    queryset = org_models.EducationProgramGroup.objects.filter(is_active=True)
    serializer_class = EducationProgramGroupSerializer

    def get_queryset(self):
        profile = self.request.user.profile

        study_year = self.request.query_params.get('study_year')
        study_form = self.request.query_params.get('study_form')
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
        queryset = self.queryset.filter(educationprogram__in=education_program_pks)

        return queryset


class EducationProgramListView(generics.ListAPIView):
    """Получить список образовательных программ
    query_params:  edu_prog_group=<uid edu_prog_group> необязательно"""

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
    """Получить список групп"""

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

        group_pks = study_plans.values('group')
        queryset = self.queryset.filter(pk__in=group_pks)

        return queryset


class CheckStudentChoices(generics.CreateAPIView):
    """Утвердить или отклонить заявки студента"""
    serializer_class = serializers.CheckStudentBidsSerializer



