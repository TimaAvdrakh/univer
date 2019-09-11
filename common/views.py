from rest_framework import generics
from . import serializers
from . import models
from organizations import models as org_models
from datetime import date
from rest_framework.response import Response
from rest_framework import status


class AcadPeriodList(generics.ListAPIView):
    """Получить список академических периодов"""
    queryset = org_models.AcadPeriod.objects.filter(is_active=True)
    serializer_class = serializers.AcadPeriodSerializer


class GetAcadPeriodsForRegister(generics.ListAPIView):
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
