from rest_framework import generics
from . import serializers
from . import models
from organizations import models as org_models
from datetime import date
from rest_framework.response import Response
from rest_framework import status
from portal_users.models import Level, AchievementType
from datetime import date


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


class RegistrationPeriodListView(generics.ListAPIView):
    """Справочник периодов регистрации
    study_year"""
    queryset = models.RegistrationPeriod.objects.filter(is_active=True)
    serializer_class = serializers.RegistrationPeriodSerializer

    def get_queryset(self):
        study_year = self.request.query_params.get('study_year')
        queryset = self.queryset.all()

        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)

            study_year_start = date(year=study_year_obj.start,
                                    month=9,
                                    day=1)
            study_year_end = date(year=study_year_obj.end,
                                  month=9,
                                  day=1)
            queryset = queryset.filter(start_date__gte=study_year_start,
                                       end_date__lte=study_year_end)
        return queryset


class StudyFormListView(generics.ListAPIView):
    """Справочник учебных форм"""
    queryset = org_models.StudyForm.objects.filter(is_active=True)
    serializer_class = serializers.StudyFormSerializer
