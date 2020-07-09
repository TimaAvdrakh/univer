from rest_framework import generics
from rest_framework import permissions
from . import serializers
from . import models
from organizations import models as org_models
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from portal_users.models import Level, AchievementType
from datetime import date
from django.utils.translation import gettext as _
from django import forms
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, Http404


class FileForm(forms.ModelForm):
    path = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = models.File
        fields = ["path"]


def replace_file(request, uid):
    if request.method == 'POST':
        file = models.File.objects.get(pk=uid)
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = request.FILES.get('path')
            file.name = new_file.name
            file.extension = new_file.name.split('.')[-1]
            file.size = new_file.size
            file.content_type = new_file.content_type
            file.path = f'upload/{new_file.name}'
            file.save()
            return JsonResponse(data={'path': f'media/{file.path.name}', 'name': file.name}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(data={'message': 'form file is invalid'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    else:
        return HttpResponse(
            content_type=b"application/pdf",
            content="Replace file"
        )


def upload(request):
    """Эндпоинт по принятию файлов от пользователей
    Принимет один файл за раз
    """
    if request.method == "POST" and request.FILES:
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES.get("path")
            form.instance.name = file.name
            form.instance.extension = file.name.split(".")[-1]
            form.instance.size = file.size
            form.instance.content_type = file.content_type
            form.instance.path = f'upload/{file.name}'
            form.save(commit=True)
            models.File.handle(file)
        else:
            raise ValidationError(
                {
                    "error": {
                        "msg": "form is invalid"
                    }
                }
            )
        return JsonResponse({"pk": [form.instance.pk]}, status=status.HTTP_200_OK)


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
        study_plan_id = request.query_params.get("study_plan")

        study_plan = org_models.StudyPlan.objects.get(pk=study_plan_id, is_active=True,)
        current_course = study_plan.current_course
        if current_course is None:
            return Response(
                {"message": "not_actual_study_plan"}, status=status.HTTP_403_FORBIDDEN
            )

        today = date.today()
        course_acad_periods = models.CourseAcadPeriodPermission.objects.filter(
            registration_period__start_date__lte=today,
            registration_period__end_date__gte=today,
            course=current_course,
        )

        serializer = self.serializer_class(course_acad_periods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetAcadPeriodsForRegisterCopyView(generics.ListAPIView):
    """Получить доступные для регистрации акам периоды
    Принимает query_param: ?study_plan="<uid study_plan>"
    """

    serializer_class = serializers.AcadPeriodSerializer

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get("study_plan")

        study_plan = org_models.StudyPlan.objects.get(pk=study_plan_id, is_active=True,)
        current_course = study_plan.current_course
        if current_course is None:
            return Response(
                {"message": "not_actual_study_plan"}, status=status.HTTP_403_FORBIDDEN
            )

        today = date.today()
        acad_period_pks = list(
            models.CourseAcadPeriodPermission.objects.filter(
                registration_period__start_date__lte=today,
                registration_period__end_date__gte=today,
                course=current_course,
            ).values_list("acad_period", flat=True)
        )

        acad_periods = org_models.AcadPeriod.objects.filter(
            pk__in=acad_period_pks, is_active=True,
        )

        serializer = self.serializer_class(acad_periods, many=True).data
        serializer.append(
            {"name": _("all period"), "uid": "all",}
        )
        return Response(serializer, status=status.HTTP_200_OK)


class GetRegPeriodAcadPeriodsView(generics.ListAPIView):  # TODO a
    """Получить акад периоды в указанном периоде регистрации
    Принимает query_param: ?study_plan="<uid study_plan>, reg_period "
    """

    serializer_class = serializers.AcadPeriodSerializer

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get("study_plan")
        reg_period = self.request.query_params.get("reg_period")

        study_plan = org_models.StudyPlan.objects.get(pk=study_plan_id, is_active=True,)
        current_course = study_plan.current_course
        if current_course is None:
            return Response(
                {"message": "not_actual_study_plan"}, status=status.HTTP_403_FORBIDDEN
            )

        acad_period_pks = models.CourseAcadPeriodPermission.objects.filter(
            registration_period_id=reg_period, course=current_course,
        ).values("acad_period")
        acad_periods = org_models.AcadPeriod.objects.filter(
            pk__in=acad_period_pks, is_active=True,
        )

        serializer = self.serializer_class(acad_periods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

    queryset = org_models.StudyPeriod.objects.filter(is_study_year=True).order_by(
        "start"
    )
    serializer_class = serializers.StudyPeriodSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        my = self.request.query_params.get("my")

        queryset = self.queryset.all()
        if my == "1":  # Если пользователь является студентом
            study_plans = org_models.StudyPlan.objects.filter(
                student=profile, is_active=True
            )
            study_year_pks = org_models.StudyYearCourse.objects.filter(
                study_plan__in=study_plans
            ).values("study_year")
            queryset = queryset.filter(pk__in=study_year_pks).order_by("start")
        return queryset


class RegistrationPeriodListView(generics.ListAPIView):
    """Справочник периодов регистрации
    study_year"""

    queryset = models.RegistrationPeriod.objects.filter(is_active=True)
    serializer_class = serializers.RegistrationPeriodSerializer

    def get_queryset(self):
        study_year = self.request.query_params.get("study_year")
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

            queryset = queryset.filter(study_year_id=study_year)
        return queryset


class StudyFormListView(generics.ListAPIView):
    """Справочник учебных форм
    study_year(!), reg_period"""

    queryset = org_models.StudyForm.objects.filter(is_active=True)
    serializer_class = serializers.StudyFormSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        study_year = self.request.query_params.get("study_year")
        reg_period = self.request.query_params.get("reg_period")  # TODO

        study_plans = org_models.StudyPlan.objects.filter(
            advisor=profile, is_active=True
        )
        if study_year:
            study_year_obj = org_models.StudyPeriod.objects.get(pk=study_year)
            study_plans = study_plans.filter(study_period__end__gt=study_year_obj.start)

        study_form_pks = study_plans.values("study_form")
        study_forms = self.queryset.filter(pk__in=study_form_pks)

        return study_forms


class TestStatusCodeView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        code = request.query_params.get("status")

        return Response({"message": "ok",}, status=int(code))


class StudyYearFromStudyPlan(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get("study_plan")
        try:
            study_plan = org_models.StudyPlan.objects.get(
                pk=study_plan_id, is_active=True
            )
        except org_models.StudyPlan.DoesNotExist:
            return Response({"message": "not_found"}, status=status.HTTP_404_NOT_FOUND)

        study_year_pks = org_models.StudyYearCourse.objects.filter(
            study_plan=study_plan, is_active=True
        ).values("study_year")
        study_years = org_models.StudyPeriod.objects.filter(
            pk__in=study_year_pks, is_study_year=True, is_active=True,
        ).order_by("start")
        serializer = serializers.StudyPeriodSerializer(instance=study_years, many=True,)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseListView(generics.ListAPIView):
    """Получить список курсов"""

    queryset = models.Course.objects.filter(is_active=True).order_by("number")
    serializer_class = serializers.CourseSerializer


class StudentDisciplineStatusListView(generics.ListAPIView):
    """Получить список cтатусов при выборе препода"""

    queryset = org_models.StudentDisciplineStatus.objects.filter(is_active=True)
    serializer_class = serializers.StudentDisciplineStatusSerializer


class NationalityViewSet(ModelViewSet):
    queryset = models.Nationality.objects.order_by("name").distinct("name").all()
    serializer_class = serializers.NationalitySerializer
    permission_classes = (permissions.AllowAny,)


class CitizenshipViewSet(ModelViewSet):
    queryset = models.Citizenship.objects.order_by("name").distinct("name").all()
    serializer_class = serializers.CitizenshipSerializer
    permission_classes = (permissions.AllowAny,)

    @action(methods=["get"], detail=False, url_path="kz", url_name="get_kz")
    def get_kz(self, request, pk=None):
        kz = self.queryset.filter(code__icontains="kz").first()
        return Response(data={"uid": kz.uid}, status=status.HTTP_200_OK)


class DocumentTypeViewSet(ModelViewSet):
    queryset = models.DocumentType.objects.order_by("name").distinct("name").all()
    serializer_class = serializers.DocumentTypeSerializer
    permission_classes = (permissions.AllowAny,)

    @action(methods=['get'], detail=False, url_path='group', url_name='get_document_type_by_group_code')
    def doc_type_grouping(self, request, pk=None):
        try:
            group = models.DocumentTypeGroup.objects.get(code=request.query_params.get('code'))
            serializer = self.serializer_class(group.types.order_by("name_ru").distinct('name_ru').all(), many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(data=self.serializer_class(self.queryset))


class GovernmentAgencyViewSet(ModelViewSet):
    queryset = models.GovernmentAgency.objects.order_by("name").all()
    serializer_class = serializers.GovernmentAgencySerializer
    permission_classes = (permissions.AllowAny,)


class InstitutionConfigViewSet(ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    queryset = models.InstitutionConfig.objects.all()
    serializer_class = serializers.InstitutionConfigSerializer

    # Любые ReST-запросы (кроме GET) запрещены
    def create(self, request, *args, **kwargs):
        return Response(data={'msg': 'config creation forbidden'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        return Response(data={'msg': 'config editing forbidden'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        return Response(data={'msg': 'config deletion forbidden'}, status=status.HTTP_403_FORBIDDEN)
