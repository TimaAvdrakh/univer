from rest_framework import generics
from . import serializers
from . import models
from organizations import models as org_models
from datetime import date
from rest_framework.response import Response
from rest_framework import status
from portal_users.models import Level, AchievementType
from datetime import date
from organizations import serializers as org_serializers
from portal_users import serializers as user_serializers
from django.utils.translation import gettext as _


class AcadPeriodListView(generics.ListAPIView):
    """Получить список академических периодов"""
    queryset = org_models.AcadPeriod.objects.filter(is_active=True)
    serializer_class = serializers.AcadPeriodSerializer


class GetAcadPeriodsForRegisterView(generics.ListAPIView):
    """Получить доступные для регистрации акам периоды
    Принимает query_param: ?study_plan="<uid study_plan>"
    """
    serializer_class = serializers.CourseAcadPeriodPermissionSerializer

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get('study_plan')

        study_plan = org_models.StudyPlan.objects.get(
            pk=study_plan_id,
            is_active=True,
        )
        current_course = study_plan.current_course
        if current_course is None:
            return Response(
                {
                    "message": "not_actual_study_plan"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        today = date.today()
        course_acad_periods = models.CourseAcadPeriodPermission.objects.filter(
            registration_period__start_date__lte=today,
            registration_period__end_date__gte=today,
            course=current_course,
        )

        serializer = self.serializer_class(course_acad_periods,
                                           many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class GetAcadPeriodsForRegisterCopyView(generics.ListAPIView):
    """Получить доступные для регистрации акам периоды
    Принимает query_param: ?study_plan="<uid study_plan>"
    """
    serializer_class = serializers.AcadPeriodSerializer

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get('study_plan')

        study_plan = org_models.StudyPlan.objects.get(
            pk=study_plan_id,
            is_active=True,
        )
        current_course = study_plan.current_course
        if current_course is None:
            return Response(
                {
                    "message": "not_actual_study_plan"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        today = date.today()
        acad_period_pks = list(models.CourseAcadPeriodPermission.objects.filter(
            registration_period__start_date__lte=today,
            registration_period__end_date__gte=today,
            course=current_course,
        ).values_list('acad_period', flat=True))

        acad_periods = org_models.AcadPeriod.objects.filter(
            pk__in=acad_period_pks,
            is_active=True,
        )

        serializer = self.serializer_class(acad_periods, many=True).data
        serializer.append(
            {
                'name': _('all period'),
                'uid': 'all',
            }
        )
        return Response(
            serializer,
            status=status.HTTP_200_OK
        )


class GetRegPeriodAcadPeriodsView(generics.ListAPIView):  # TODO a
    """Получить акад периоды в указанном периоде регистрации
    Принимает query_param: ?study_plan="<uid study_plan>, reg_period "
    """
    serializer_class = serializers.AcadPeriodSerializer

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get('study_plan')
        reg_period = self.request.query_params.get('reg_period')

        study_plan = org_models.StudyPlan.objects.get(
            pk=study_plan_id,
            is_active=True,
        )
        current_course = study_plan.current_course
        if current_course is None:
            return Response(
                {
                    "message": "not_actual_study_plan"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        acad_period_pks = models.CourseAcadPeriodPermission.objects.filter(
            registration_period_id=reg_period,
            course=current_course,
        ).values('acad_period')
        acad_periods = org_models.AcadPeriod.objects.filter(
            pk__in=acad_period_pks,
            is_active=True,
        )

        serializer = self.serializer_class(acad_periods,
                                           many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class LevelListView(generics.ListAPIView):
    """Получить список уровней"""
    queryset = Level.objects.filter(is_active=True)
    serializer_class = serializers.LevelSerializer


class AchievementTypeListView(generics.ListAPIView):
    """Получить список видов достижений"""
    queryset = AchievementType.objects.filter(is_active=True)
    serializer_class = serializers.AchievementTypeSerializer


class StudyYearListView(generics.ListAPIView):
    """Справочник учебных годов"""
    queryset = org_models.StudyPeriod.objects.filter(is_study_year=True).order_by('start')
    serializer_class = serializers.StudyPeriodSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        my = self.request.query_params.get('my')

        queryset = self.queryset.all()

        if my == '1':
            study_plans = org_models.StudyPlan.objects.filter(student=profile,
                                                              is_active=True)
            study_year_pks = org_models.StudyYearCourse.objects.filter(study_plan__in=study_plans).values('study_year')
            queryset = queryset.filter(pk__in=study_year_pks).order_by('start')

        return queryset


class RegistrationPeriodListView(generics.ListAPIView):
    """Справочник периодов регистрации
    study_year"""
    queryset = models.RegistrationPeriod.objects.filter(is_active=True)
    serializer_class = serializers.RegistrationPeriodSerializer

    def get_queryset(self):
        study_year = self.request.query_params.get('study_year')
        queryset = self.queryset.all()

        if study_year:
            # study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            # study_year_start = date(year=study_year_obj.start,
            #                         month=9,
            #                         day=1)
            # study_year_end = date(year=study_year_obj.end,
            #                       month=9,
            #                       day=1)
            # queryset = queryset.filter(start_date__year__gte=study_year_obj.start,
            #                            end_date__lte=study_year_end)

            queryset = queryset.select_related('study_year_id').filter(study_year_id=study_year)
        return queryset


class StudyFormListView(generics.ListAPIView):
    """Справочник учебных форм
    study_year(!), reg_period"""

    queryset = org_models.StudyForm.objects.filter(is_active=True)
    serializer_class = serializers.StudyFormSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        study_year = self.request.query_params.get('study_year')
        reg_period = self.request.query_params.get('reg_period')  # TODO

        study_plans = org_models.StudyPlan.objects.filter(advisor=profile,
                                                          is_active=True)
        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plans = study_plans.filter(study_period__end__gt=study_year_obj.start)

        study_form_pks = study_plans.values('study_form')
        study_forms = self.queryset.filter(pk__in=study_form_pks)

        return study_forms


class TestStatusCodeView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        code = request.query_params.get('status')

        return Response(
            {
                'message': 'ok',
            },
            status=int(code)
        )


class StudyYearFromStudyPlan(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get('study_plan')
        try:
            study_plan = org_models.StudyPlan.objects.get(pk=study_plan_id,
                                                          is_active=True)
        except org_models.StudyPlan.DoesNotExist:
            return Response(
                {
                    'message': 'not_found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        study_year_pks = org_models.StudyYearCourse.objects.filter(
            study_plan=study_plan,
            is_active=True
        ).values('study_year')
        study_years = org_models.StudyPeriod.objects.filter(
            pk__in=study_year_pks,
            is_study_year=True,
            is_active=True,
        ).order_by('start')
        serializer = serializers.StudyPeriodSerializer(
            instance=study_years,
            many=True,
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CourseListView(generics.ListAPIView):
    """Получить список курсов"""
    queryset = models.Course.objects.filter(is_active=True)
    serializer_class = serializers.CourseSerializer


class StudentDisciplineStatusListView(generics.ListAPIView):
    """Получить список cтатусов при выборе препода"""
    queryset = org_models.StudentDisciplineStatus.objects.filter(is_active=True)
    serializer_class = serializers.StudentDisciplineStatusSerializer
