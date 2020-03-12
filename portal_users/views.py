from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from . import models
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from organizations import models as org_models
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions as rest_permissions
from . import permissions
from .utils import get_current_study_year
from portal.curr_settings import student_discipline_info_status, not_choosing_load_types2, CYCLE_DISCIPLINE
from datetime import date
from common import models as common_models
from rest_framework.views import APIView


class LoginView(generics.CreateAPIView):
    """Логин"""

    permission_classes = ()
    authentication_classes = ()
    serializer_class = serializers.LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cd = serializer.validated_data
        user = authenticate(request, username=cd["username"], password=cd["password"])
        if user is not None:
            profile_serializer = serializers.ProfileDetailSerializer(instance=user.profile)
            profile_data = profile_serializer.data
            data = {
                "user": profile_data,
                "firstLogin": user.last_login is None or (not user.profile.password_changed),
            }
            login(request, user)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "wrong_username_or_password"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    """Выйти из системы"""

    def post(self, request):
        logout(request)
        return Response({"message": "ok"}, status=status.HTTP_200_OK)


class PasswordChangeView(generics.CreateAPIView):
    """Сменить пароль"""

    serializer_class = serializers.PasswordChangeSerializer
    queryset = User.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            login(request, user)
            return Response(
                {
                    'message': 1  # Успешно
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response({'message': serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(generics.CreateAPIView):
    """Забыли пароль"""

    permission_classes = ()
    authentication_classes = ()
    queryset = models.ResetPassword.objects.all()
    serializer_class = serializers.ForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": 1}, status=status.HTTP_200_OK)  # Успешно


class ResetPasswordView(generics.CreateAPIView):
    """Восстановить пароль"""

    # permission_classes = ()
    # authentication_classes = ()
    serializer_class = serializers.ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": 1}, status=status.HTTP_200_OK)  # Успешно


class TestView(APIView):
    def get(self, request):
        return Response({"isAuth": "ok"}, status=status.HTTP_200_OK)


class UserRegisterView(generics.CreateAPIView):
    """Регистрация пользователей из 1С"""

    permission_classes = ()
    authentication_classes = ()
    queryset = models.Profile.objects.all()
    serializer_class = serializers.UserCreateSerializer

    def create(self, request, *args, **kwargs):
        org_token = request.data.get("org_token", None)
        if not org_token:
            return Response({"status": 0,}, status=status.HTTP_400_BAD_REQUEST)

        if not models.OrganizationToken.objects.filter(
            token=org_token, is_active=True
        ).exists():
            return Response({"status": 0,}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": 1,}, status=status.HTTP_201_CREATED)


class StudentDisciplineForRegListView(generics.ListAPIView):
    """Получить список дисциплин для регистрации
       Принимает: query_params: ?study_plan=<uid study_plan>&acad_period=<uid acad_period>
    """

    serializer_class = serializers.StudentDisciplineSerializer
    permission_classes = (
        IsAuthenticated,
        permissions.StudyPlanPermission,
    )

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get("study_plan")
        acad_period_id = request.query_params.get("acad_period")
        study_year_id = request.query_params.get("study_year")

        try:
            study_plan = org_models.StudyPlan.objects.get(
                pk=study_plan_id, is_active=True,
            )
        except org_models.StudyPlan.DoesNotExist:
            return Response({"message": "not_found",}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(self.request, study_plan)

        try:
            org_models.StudentDisciplineInfo.objects.get(
                study_plan_id=study_plan_id, acad_period_id=acad_period_id,
            )
        except org_models.StudentDisciplineInfo.DoesNotExist:  # Создаем StudentDisciplineInfo если не создан
            org_models.StudentDisciplineInfo.objects.create(
                student=study_plan.student,
                study_plan_id=study_plan_id,
                acad_period_id=acad_period_id,
                status_id=student_discipline_info_status["not_started"],
            )

        student_disciplines = (
            org_models.StudentDiscipline.objects.filter(
                study_plan_id=study_plan_id,
                acad_period_id=acad_period_id,
                study_year_id=study_year_id,
                is_active=True,
            )
            .exclude(load_type__load_type2__in=not_choosing_load_types2)
            .order_by("discipline")
        )

        serializer = self.serializer_class(
            student_disciplines, context={"study_year_id": study_year_id}, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentDisciplineForRegListCopyView(generics.ListAPIView):
    """Получить список дисциплин для регистрации
       Принимает: query_params: ?study_plan=<uid study_plan>&acad_period=<uid acad_period>
    """
    serializer_class = serializers.StudentDisciplineListSerializer
    permission_classes = (
        IsAuthenticated,
        permissions.StudyPlanPermission,
    )

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get('study_plan')
        acad_period_id = request.query_params.get('acad_period')
        study_year_id = request.query_params.get('study_year')
        reg_period_id = self.request.query_params.get('reg_period')

        try:
            study_plan = org_models.StudyPlan.objects.get(
                pk=study_plan_id,
                is_active=True,
            )
        except org_models.StudyPlan.DoesNotExist:
            return Response(
                {
                    'message': 'not_found',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(self.request,
                                      study_plan)

        is_advisor = False
        if study_plan.advisor == request.user.profile:
            is_advisor = True

        if reg_period_id and is_advisor:
            """Передаем все дисциплины группой"""
            current_course = study_plan.current_course
            if current_course is None:
                return Response(
                    {
                        "message": "not_actual_study_plan"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            acad_period_pks = common_models.CourseAcadPeriodPermission.objects.filter(
                registration_period_id=reg_period_id,
                course=current_course,
            ).values('acad_period')
            acad_periods = org_models.AcadPeriod.objects.filter(
                pk__in=acad_period_pks,
                is_active=True,
            )

            resp = []

            for acad_period in acad_periods:
                try:
                    org_models.StudentDisciplineInfo.objects.get(
                        study_plan_id=study_plan_id,
                        acad_period=acad_period,
                    )
                except org_models.StudentDisciplineInfo.DoesNotExist:  # Создаем StudentDisciplineInfo если не создан
                    org_models.StudentDisciplineInfo.objects.create(
                        student=study_plan.student,
                        study_plan_id=study_plan_id,
                        acad_period=acad_period,
                        status_id=student_discipline_info_status["not_started"],
                    )

                student_disciplines = org_models.StudentDiscipline.objects.filter(
                    study_plan=study_plan,
                    acad_period=acad_period,
                    study_year_id=study_year_id,
                    is_active=True,
                ).exclude(load_type__load_type2__in=not_choosing_load_types2).distinct('discipline').order_by('discipline')

                if not student_disciplines.exists():
                    """
                    Если дисциплин студентов нет, то исключим акад период из ответа
                    """
                    continue

                serializer = self.serializer_class(student_disciplines, context={'study_year_id': study_year_id}, many=True)

                item = {
                    'name': acad_period.repr_name,
                    'disciplines': serializer.data,
                }
                resp.append(item)

            return Response(
                resp,
                status=status.HTTP_200_OK
            )
        elif acad_period_id:
            try:
                org_models.StudentDisciplineInfo.objects.get(
                    study_plan_id=study_plan_id,
                    acad_period_id=acad_period_id,
                )
            except org_models.StudentDisciplineInfo.DoesNotExist:  # Создаем StudentDisciplineInfo если не создан
                org_models.StudentDisciplineInfo.objects.create(
                    student=study_plan.student,
                    study_plan_id=study_plan_id,
                    acad_period_id=acad_period_id,
                    status_id=student_discipline_info_status["not_started"],
                )

            student_disciplines = org_models.StudentDiscipline.objects.filter(
                study_plan_id=study_plan_id,
                acad_period_id=acad_period_id,
                # study_year_id=study_year_id,
                is_active=True,
            ).exclude(load_type__load_type2__in=not_choosing_load_types2).distinct('discipline').order_by('discipline')

            serializer = self.serializer_class(student_disciplines,
                                               context={'study_year_id': study_year_id},
                                               many=True)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        elif not is_advisor:
            current_course = study_plan.current_course
            if current_course is None:
                return Response(
                    {
                        "message": "not_actual_study_plan"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            today = date.today()
            acad_period_pks = common_models.CourseAcadPeriodPermission.objects.filter(
                registration_period__start_date__lte=today,
                registration_period__end_date__gte=today,
                course=current_course,
            ).values('acad_period')
            acad_periods = org_models.AcadPeriod.objects.filter(
                pk__in=acad_period_pks,
                is_active=True,
            )
            resp = []

            if acad_period_pks:

                for acad_period in acad_periods:
                    try:
                        org_models.StudentDisciplineInfo.objects.get(
                            study_plan_id=study_plan_id,
                            acad_period=acad_period,
                        )
                    except org_models.StudentDisciplineInfo.DoesNotExist:  # Создаем StudentDisciplineInfo если не создан
                        org_models.StudentDisciplineInfo.objects.create(
                            student=study_plan.student,
                            study_plan_id=study_plan_id,
                            acad_period=acad_period,
                            status_id=student_discipline_info_status["not_started"],
                        )

                    student_disciplines = org_models.StudentDiscipline.objects.filter(
                        study_plan=study_plan,
                        acad_period=acad_period,
                        study_year_id=study_year_id,
                        is_active=True,
                    ).exclude(load_type__load_type2__in=not_choosing_load_types2). \
                        distinct('discipline').order_by('discipline')

                    if not student_disciplines.exists():
                        """
                        Если дисциплин студентов нет, то исключим акад период из ответа
                        """
                        continue

                    serializer = self.serializer_class(student_disciplines,
                                                       context={'study_year_id': study_year_id},
                                                       many=True)

                    item = {
                        'name': acad_period.repr_name,
                        'disciplines': serializer.data,
                    }
                    resp.append(item)

                return Response(
                    resp,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'uid': study_plan.advisor_id,
                        'error': 400
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


class MyStudyPlanListView(generics.ListAPIView):
    """Получить список моих актуальных учебных планов"""

    queryset = org_models.StudyPlan.objects.filter(is_active=True)
    serializer_class = serializers.StudyPlanSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        current_study_year = get_current_study_year()
        queryset = self.queryset.filter(
            student=profile,
            study_period__end__gt=current_study_year.get("start"),
            is_active=True,
        )
        return queryset


class ChooseTeacherView(generics.UpdateAPIView):
    """Выбрать преподавателя"""

    permission_classes = (IsAuthenticated, permissions.StudentDisciplinePermission)
    # authentication_classes = (CsrfExemptSessionAuthentication,)
    queryset = org_models.StudentDiscipline.objects.filter(is_active=True)
    serializer_class = serializers.ChooseTeacherSerializer

    def put(self, request, *args, pk=None, **kwargs):
        try:
            student_discipline = self.queryset.get(pk=pk)
        except org_models.StudentDiscipline.DoesNotExist:
            return Response({"message": "not_found",}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, student_discipline)
        serializer = self.serializer_class(
            data=request.data, instance=student_discipline, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "ok",}, status=status.HTTP_200_OK)

      
class MyGroupListView(generics.RetrieveAPIView):
    """Получить группу выбранного учебного плана"""
    serializer_class = serializers.GroupDetailSerializer
    permission_classes = (
        IsAuthenticated,
        permissions.StudyPlanPermission,
    )

    def get(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get('study_plan')
        try:
            study_plan = org_models.StudyPlan.objects.get(
                pk=study_plan_id,
                is_active=True,
            )
            self.check_object_permissions(request, study_plan)
        except org_models.StudyPlan.DoesNotExist:
            return Response(
                {
                    'message': 'not_found'
                },
                status=400
            )
        serializer = self.serializer_class(study_plan.group,
                                           context={'request': request})

        return Response(
            serializer.data,
            status=200
        )


class NotifyAdviser(generics.CreateAPIView):
    """Уведомлять адвайзера о том, что студент завершил регистрацию на дисциплины"""

    serializer_class = serializers.NotifyAdviserSerializer
    permission_classes = (
        IsAuthenticated,
        permissions.StudyPlanPermission,
    )

    def create(self, request, *args, **kwargs):
        study_plan_id = request.data.get("study_plan")
        try:
            study_plan = org_models.StudyPlan.objects.get(
                pk=study_plan_id, is_active=True,
            )
        except org_models.StudyPlan.DoesNotExist:
            return Response({"message": "not_found",}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request,
                                      study_plan)
        datas = request.data
        datas['status'] = True
        serializer = self.serializer_class(data=datas)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "ok"}, status=status.HTTP_200_OK)


class StudentAllDisciplineListView(generics.ListAPIView):
    """Получить список дисциплин студента
    Принимает: query_params: ?study_plan=<uid study_plan>
    """

    # &acad_period=<uid acad_period>
    permission_classes = (
        IsAuthenticated,
        permissions.StudyPlanPermission,
    )
    serializer_class = serializers.StudentDisciplineShortSerializer2

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get("study_plan")
        # acad_period_id = request.query_params.get('acad_period')

        try:
            study_plan = org_models.StudyPlan.objects.get(
                pk=study_plan_id, is_active=True,
            )
        except org_models.StudyPlan.DoesNotExist:
            return Response({"message": "not_found",}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(self.request, study_plan)

        acad_period_pks = org_models.StudentDiscipline.objects.filter(
            study_plan_id=study_plan_id, is_active=True,
        ).values("acad_period")

        acad_periods = org_models.AcadPeriod.objects.filter(pk__in=acad_period_pks)

        resp = []

        for acad_period in acad_periods:
            student_disciplines = org_models.StudentDiscipline.objects.filter(
                study_plan_id=study_plan_id,
                acad_period=acad_period,
                # is_active=True,
            ).order_by('discipline')
            serializer = self.serializer_class(student_disciplines,
                                               many=True)
            item_key = acad_period.repr_name
            item = {
                'name_period': item_key,
                'disciplines': serializer.data
            }
            resp.append(item)

        return Response(resp, status=status.HTTP_200_OK)


class ProfileDetailView(generics.RetrieveAPIView):
    """Получить профиль пользователя"""

    queryset = models.Profile.objects.filter(is_active=True)
    serializer_class = serializers.ProfileFullSerializer


class ContactEditView(generics.UpdateAPIView):
    """Редактировать контактные данные"""

    permission_classes = (
        IsAuthenticated,
        permissions.ProfilePermission,
    )
    queryset = models.Profile.objects.filter(is_active=True)
    serializer_class = serializers.ProfileContactEditSerializer


class InterestsEditView(generics.UpdateAPIView):
    """Редактировать интересы"""

    permission_classes = (
        # IsAuthenticated,
        permissions.ProfilePermission,
    )
    queryset = models.Profile.objects.filter(is_active=True)
    serializer_class = serializers.ProfileInterestsEditSerializer


class AchievementsEditView(generics.UpdateAPIView):
    """Редактировать достижения"""

    permission_classes = (
        IsAuthenticated,
        permissions.ProfilePermission,
    )
    queryset = models.Profile.objects.filter(is_active=True)
    serializer_class = serializers.ProfileAchievementsEditSerializer


class AvatarUploadView(generics.CreateAPIView):
    """Загрузка аватар"""

    serializer_class = serializers.AvatarSerializer
    queryset = models.Profile.objects.filter(is_active=True)


class RoleGetView(APIView):
    """Получить своих ролей"""

    serializer_class = serializers.ProfileDetailSerializer
    permission_classes = ()

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "not_authenticated"}, status=status.HTTP_200_OK)

        if request.user.last_login is None or (
            not request.user.profile.password_changed
        ):
            return Response({"message": "not_authenticated"}, status=status.HTTP_200_OK)

        serializer = self.serializer_class(instance=request.user.profile)

        return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.viewsets import ModelViewSet


class GenderViewSet(ModelViewSet):
    queryset = models.Gender.objects.all()
    serializer_class = serializers.GenderSerializer
    permission_classes = (rest_permissions.AllowAny,)


class MaritalStatusViewSet(ModelViewSet):
    queryset = models.MaritalStatus.objects.all()
    serializer_class = serializers.MaritalStatusSerializer
    permission_classes = (rest_permissions.AllowAny,)


class PhoneTypeViewSet(ModelViewSet):
    queryset = models.PhoneType.objects.all()
    serializer_class = serializers.PhoneTypeSerializer
    permission_classes = (rest_permissions.AllowAny,)

    
class ChooseControlFormListView(generics.ListAPIView):
    """Получить список дисциплин для выбора формы контроля если цикл - Итоговая аттестация
       Принимает: query_params: ?study_plan=<uid study_plan>&acad_period=<uid acad_period>
    """
    serializer_class = serializers.StudentDisciplineControlFormSerializer
    permission_classes = (
        IsAuthenticated,
        permissions.StudyPlanPermission,
    )

    def list(self, request, *args, **kwargs):

        study_plan_id = request.query_params.get('study_plan')
        acad_period_id = request.query_params.get('acad_period')
        study_year_id = request.query_params.get('study_year')
        reg_period_id = self.request.query_params.get('reg_period')

        try:
            study_plan = org_models.StudyPlan.objects.get(
                pk=study_plan_id,
                is_active=True,
            )
        except org_models.StudyPlan.DoesNotExist:
            return Response(
                {
                    'message': 'not_found',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(self.request,
                                      study_plan)

        is_advisor = False
        if study_plan.advisor == request.user.profile:
            is_advisor = True

        if reg_period_id and is_advisor:
            """Передаем все дисциплины группой"""
            current_course = study_plan.current_course
            if current_course is None:
                return Response(
                    {
                        "message": "not_actual_study_plan"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            acad_period_pks = common_models.CourseAcadPeriodPermission.objects.filter(
                registration_period_id=reg_period_id,
                course=current_course,
            ).values('acad_period')
            acad_periods = org_models.AcadPeriod.objects.filter(
                pk__in=acad_period_pks,
                is_active=True,
            )

            resp = []

            for acad_period in acad_periods:
                try:
                    org_models.StudentDisciplineInfo.objects.get(
                        study_plan_id=study_plan_id,
                        acad_period=acad_period,
                    )
                except org_models.StudentDisciplineInfo.DoesNotExist:  # Создаем StudentDisciplineInfo если не создан
                    org_models.StudentDisciplineInfo.objects.create(
                        student=study_plan.student,
                        study_plan_id=study_plan_id,
                        acad_period=acad_period,
                        status_id=student_discipline_info_status["not_started"],
                    )

                student_disciplines = org_models.StudentDiscipline.objects.filter(
                    study_plan=study_plan,
                    acad_period=acad_period,
                    study_year_id=study_year_id,
                    is_active=True,
                    cycle_id=CYCLE_DISCIPLINE['itog_attest'],
                ).order_by('discipline')

                if not student_disciplines.exists():
                    """
                    Если дисциплин студентов нет, то исключим акад период из ответа
                    """
                    continue

                serializer = self.serializer_class(student_disciplines,
                                                   context={'study_year_id': study_year_id},
                                                   many=True)

                item = {
                    'name': acad_period.repr_name,
                    'disciplines': serializer.data,
                }
                resp.append(item)

            return Response(
                resp,
                status=status.HTTP_200_OK
            )
        elif acad_period_id:
            try:
                org_models.StudentDisciplineInfo.objects.get(
                    study_plan_id=study_plan_id,
                    acad_period_id=acad_period_id,
                )
            except org_models.StudentDisciplineInfo.DoesNotExist:  # Создаем StudentDisciplineInfo если не создан
                org_models.StudentDisciplineInfo.objects.create(
                    student=study_plan.student,
                    study_plan_id=study_plan_id,
                    acad_period_id=acad_period_id,
                    status_id=student_discipline_info_status["not_started"],
                )

            student_disciplines = org_models.StudentDiscipline.objects.filter(
                study_plan_id=study_plan_id,
                acad_period_id=acad_period_id,
                study_year_id=study_year_id,
                is_active=True,
                cycle_id=CYCLE_DISCIPLINE['itog_attest'],
            ).order_by('discipline')

            serializer = self.serializer_class(student_disciplines,
                                               context={'study_year_id': study_year_id},
                                               many=True)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        elif not is_advisor:
            current_course = study_plan.current_course
            if current_course is None:
                return Response(
                    {
                        "message": "not_actual_study_plan"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            today = date.today()
            acad_period_pks = common_models.CourseAcadPeriodPermission.objects.filter(
                registration_period__start_date__lte=today,
                registration_period__end_date__gte=today,
                course=current_course,
            ).values('acad_period')
            acad_periods = org_models.AcadPeriod.objects.filter(
                pk__in=acad_period_pks,
                is_active=True,
            )
            resp = []

            for acad_period in acad_periods:
                try:
                    org_models.StudentDisciplineInfo.objects.get(
                        study_plan_id=study_plan_id,
                        acad_period=acad_period,
                    )
                except org_models.StudentDisciplineInfo.DoesNotExist:  # Создаем StudentDisciplineInfo если не создан
                    org_models.StudentDisciplineInfo.objects.create(
                        student=study_plan.student,
                        study_plan_id=study_plan_id,
                        acad_period=acad_period,
                        status_id=student_discipline_info_status["not_started"],
                    )

                student_disciplines = org_models.StudentDiscipline.objects.filter(
                    study_plan=study_plan,
                    acad_period=acad_period,
                    study_year_id=study_year_id,
                    is_active=True,
                    cycle_id=CYCLE_DISCIPLINE['itog_attest'],
                ).order_by('discipline')

                if not student_disciplines.exists():
                    """
                    Если дисциплин студентов нет, то исключим акад период из ответа
                    """
                    continue

                serializer = self.serializer_class(student_disciplines,
                                                   context={'study_year_id': study_year_id},
                                                   many=True)

                item = {
                    'name': acad_period.repr_name,
                    'disciplines': serializer.data,
                }
                resp.append(item)

            return Response(
                resp,
                status=status.HTTP_200_OK
            )


class ChooseFormControlView(generics.UpdateAPIView):
    permission_classes = (
        IsAuthenticated,
        # permissions.DisciplineCreditPermission,
    )
    queryset = org_models.DisciplineCredit.objects.filter(is_active=True)
    serializer_class = serializers.ChooseControlFormSerializer

    def update(self, request, *args, **kwargs):
        data = request.data
        partial = kwargs.pop('partial', False)
        try:
            if request.user.profile.role.is_student:
                data['status'] = org_models.StudentDisciplineStatus.objects.get(number=2).uid
            elif request.user.profile.role.is_supervisor:
                data['status'] = org_models.StudentDisciplineStatus.objects.get(number=5).uid
                data['teacher'] = request.user.profile.uid
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class StudentStatusListView(generics.ListAPIView):
    """
    Список статуса студентов для эдвайзера
    """
    queryset = models.StudentStatus.objects
    serializer_class = serializers.StudentStatusListSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(is_active=True).order_by('name')
        return queryset


class GenderListView(generics.ListAPIView):
    """
    Список пола пользователей
    """
    queryset = models.Gender.objects
    serializer_class = serializers.GenderListSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(is_active=True).order_by('name')
        return queryset


class CitizenshipListView(generics.ListAPIView):
    """
    Список национальностей пользователей
    """
    queryset = common_models.Citizenship.objects
    serializer_class = serializers.CitizenshipListSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(is_active=True).order_by('name')
        student_pks = org_models.StudyPlan.objects.filter(advisor=self.request.user.profile).values('student')
        citizenship_pks = models.Profile.objects.filter(pk__in=student_pks).values('citizenship')
        queryset = queryset.filter(pk__in=citizenship_pks)

        return queryset
