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
from portal.curr_settings import student_discipline_info_status


class StudyPlansListView(generics.ListAPIView):
    """
    Получение учебных планов, query_params: study_year, study_form, faculty, cathedra, edu_prog_group, edu_prog, course, group
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
    Получение дисциплин студента, query_params: study_plan, acad_period, status, short (если значение 1, вернет только первые три записи)
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
    """Получить список акад периодов по курсу и периоду регистрации, query_params: reg_period, course"""

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
    """Получить список факультетов доступных для эдвайзеру, query_params: study_year, study_form"""
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
    """Получить список групп образовательных программ, query_params: study_year, study_form, faculty, cathedra"""

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
    """Получить список образовательных программ, query_params:  edu_prog_group=<uid edu_prog_group> необязательно"""

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
    """Получить список групп, query_params: study_year, study_form, faculty, cathedra, edu_prog, course"""

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


class FilteredStudentsListView(generics.ListAPIView):
    """Фильтровать студентов для селекта (Эдвайзер)"""
    serializer_class = ProfileShortSerializer

    def get_queryset(self):
        request = self.request

        study_year = request.query_params.get('study_year')
        faculty = request.query_params.get('faculty')
        speciality = request.query_params.get('speciality')  # TODO АПИ для получения специальностей
        edu_prog = request.query_params.get('edu_prog')
        group = request.query_params.get('group')

        study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
        student_pks = org_models.StudyPlan.objects.filter(
            group_id=group,
            speciality_id=speciality,
            faculty_id=faculty,
            education_program_id=edu_prog,
            study_period__end__gt=study_year_obj.start,
            is_active=True,
        ).values('student')
        students = Profile.objects.filter(pk__in=student_pks)

        return students


class GetStudyPlanView(generics.RetrieveAPIView):
    """Получает учебный план студента для отчета (Эдвайзер)"""
    serializer_class = serializers.StudyPlanDetailSerializer

    def get(self, request, *args, **kwargs):

        # reg_period = self.request.query_params.get('reg_period')
        # acad_period = self.request.query_params.get('acad_period')
        # edu_prog_group = self.request.query_params.get('edu_prog_group')

        study_year = request.query_params.get('study_year')
        faculty = request.query_params.get('faculty')
        speciality = request.query_params.get('speciality')  # TODO АПИ для получения специальностей
        edu_prog = request.query_params.get('edu_prog')
        group = request.query_params.get('group')
        student = request.query_params.get('student')

        try:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)

            study_plan = org_models.StudyPlan.objects.get(
                student_id=student,
                group_id=group,
                speciality_id=speciality,
                faculty_id=faculty,
                education_program_id=edu_prog,
                study_period__end__gt=study_year_obj.start,
                is_active=True,
            )
        except org_models.StudyPlan.DoesNotExist:
            return Response(
                {
                    'message': 0  # Учебный план не найден
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(instance=study_plan)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ConfirmedStudentDisciplineListView(generics.ListAPIView):
    serializer_class = serializers.ConfirmedStudentDisciplineShortSerializer

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get('study_plan')
        acad_period_id = self.request.query_params.get('acad_period')

        study_plan = org_models.StudyPlan.objects.get(pk=study_plan_id)

        resp = []

        if acad_period_id:
            acad_period = org_models.AcadPeriod.objects.get(pk=acad_period_id)

            try:
                StudentDisciplineInfo.objects.get(
                    study_plan=study_plan,
                    acad_period_id=acad_period_id,
                    status_id=student_discipline_info_status['confirmed'],
                )
            except StudentDisciplineInfo.DoesNotExist:
                return Response(
                    {
                        'message': 'not_found',
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            student_disciplines = org_models.StudentDiscipline.objects.filter(
                study_plan_id=study_plan_id,
                acad_period_id=acad_period_id,
                is_active=True,
            )
            serializer = self.serializer_class(student_disciplines,
                                               many=True)
            item_key = acad_period.name
            item = {
                item_key: serializer.data
            }
            resp.append(item)

        else:
            acad_period_pks = StudentDisciplineInfo.objects.filter(
                study_plan=study_plan,
                status_id=student_discipline_info_status['confirmed'],
            ).values('acad_period')

            acad_periods = org_models.AcadPeriod.objects.filter(pk__in=acad_period_pks)

            for acad_period in acad_periods:
                student_disciplines = org_models.StudentDiscipline.objects.filter(
                    study_plan_id=study_plan_id,
                    acad_period=acad_period,
                    is_active=True,
                )
                serializer = self.serializer_class(student_disciplines,
                                                   many=True)
                item_key = acad_period.name
                item = {
                    item_key: serializer.data
                }
                resp.append(item)

        return Response(
            resp,
            status=status.HTTP_200_OK
        )



