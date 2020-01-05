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
from . import permissions
from .utils import get_current_study_year
from common.csrf_exempt_auth_class import CsrfExemptSessionAuthentication
from portal.curr_settings import student_discipline_info_status, current_site, not_choosing_load_types2


class LoginView(generics.CreateAPIView):
    """Логин"""
    permission_classes = ()
    authentication_classes = ()
    serializer_class = serializers.LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cd = serializer.validated_data
        user = authenticate(request,
                            username=cd['username'],
                            password=cd['password'])
        if user is not None:
            profile_serializer = serializers.ProfileDetailSerializer(instance=user.profile)
            profile_data = profile_serializer.data
            if profile_data['avatar'] is not None:
                profile_data['avatar'] = current_site + profile_data['avatar']

            data = {
                'user': profile_data,
                'firstLogin': user.last_login is None or (not user.profile.password_changed)
            }

            login(request, user)

            return Response(
                data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'error': 'wrong_username_or_password'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """Выйти из системы"""

    def post(self, request):
        logout(request)
        return Response(
            {
                'message': 'ok'
            },
            status=status.HTTP_200_OK
        )


class PasswordChangeView(generics.CreateAPIView):
    """Сменить пароль"""
    serializer_class = serializers.PasswordChangeSerializer
    queryset = User.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        login(request, user)
        return Response(
            {
                'message': 1  # Успешно
            },
            status=status.HTTP_200_OK
        )


class ForgetPasswordView(generics.CreateAPIView):
    """Забыли пароль"""
    permission_classes = ()
    authentication_classes = ()
    queryset = models.ResetPassword.objects.all()
    serializer_class = serializers.ForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                'message': 1  # Успешно
            },
            status=status.HTTP_200_OK
        )


class ResetPasswordView(generics.CreateAPIView):
    """Восстановить пароль"""
    permission_classes = ()
    authentication_classes = ()
    serializer_class = serializers.ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                'message': 1  # Успешно
            },
            status=status.HTTP_200_OK
        )


class TestView(APIView):
    def get(self, request):
        return Response(
            {
                'isAuth': 'ok'
            },
            status=status.HTTP_200_OK
        )


class UserRegisterView(generics.CreateAPIView):
    """Регистрация пользователей из 1С"""
    permission_classes = ()
    authentication_classes = ()
    queryset = models.Profile.objects.all()
    serializer_class = serializers.UserCreateSerializer

    def create(self, request, *args, **kwargs):
        org_token = request.data.get('org_token', None)
        if not org_token:
            return Response(
                {
                    'status': 0,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not models.OrganizationToken.objects.filter(token=org_token,
                                                       is_active=True).exists():
            return Response(
                {
                    'status': 0,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'status': 1,
            },
            status=status.HTTP_201_CREATED
        )


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
        study_plan_id = request.query_params.get('study_plan')
        acad_period_id = request.query_params.get('acad_period')
        study_year_id = request.query_params.get('study_year')

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
            is_active=True,
        ).exclude(load_type__load_type2__in=not_choosing_load_types2).order_by('discipline')  # TODO TEST

        serializer = self.serializer_class(student_disciplines,
                                           context={'study_year_id': study_year_id},
                                           many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # def list(self, request, *args, **kwargs):
    #     profile = request.user.profile

    # current_acad_period = "d922e730-2b90-4296-9802-1853020b0357"  # 1 trimestr

    # current_study_year = get_current_study_year()
    # study_plans = org_models.StudyPlan.objects.filter(
    #     student=profile,
    #     study_period__end__gt=current_study_year.get('start'),
    #     is_active=True,
    # )
    # resp = []
    # for study_plan in study_plans:
    #     student_disciplines = org_models.StudentDiscipline.objects.filter(
    #         study_plan=study_plan,
    #         acad_period_id=current_acad_period,
    #     )
    #     serializer = self.serializer_class(student_disciplines,
    #                                        many=True)
    #     item = {
    #         "study_plan_id": study_plan.pk,
    #         'speciality_name': study_plan.speciality.name,
    #         'active': False,
    #         'disciplines': serializer.data,
    #     }
    #     resp.append(item)
    #
    # return Response(
    #     resp,
    #     status=status.HTTP_200_OK
    # )


class MyStudyPlanListView(generics.ListAPIView):
    """Получить список моих актуальных учебных планов"""
    queryset = org_models.StudyPlan.objects.filter(is_active=True)
    serializer_class = serializers.StudyPlanSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        current_study_year = get_current_study_year()
        queryset = self.queryset.filter(
            student=profile,
            study_period__end__gt=current_study_year.get('start'),
            is_active=True,
        )
        return queryset


class ChooseTeacherView(generics.UpdateAPIView):
    """Выбрать преподавателя"""
    permission_classes = (
        IsAuthenticated,
        permissions.StudentDisciplinePermission
    )
    # authentication_classes = (CsrfExemptSessionAuthentication,)
    queryset = org_models.StudentDiscipline.objects.filter(is_active=True)
    serializer_class = serializers.ChooseTeacherSerializer

    def put(self, request, *args, pk=None, **kwargs):
        try:
            student_discipline = self.queryset.get(pk=pk)
        except org_models.StudentDiscipline.DoesNotExist:
            return Response(
                {
                    "message": "not_found",
                },
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request,
                                      student_discipline)
        serializer = self.serializer_class(data=request.data,
                                           instance=student_discipline,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "ok",
            },
            status=status.HTTP_200_OK
        )


class MyGroupListView(generics.ListAPIView):
    """Получить инфо о моих группах"""
    serializer_class = serializers.GroupDetailSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        current_study_year = get_current_study_year()

        my_group_pks = org_models.StudyPlan.objects.filter(
            student=profile,
            study_period__end__gt=current_study_year.get('start'),
            is_active=True
        ).values('group')
        my_groups = org_models.Group.objects.filter(
            pk__in=my_group_pks,
            is_active=True,
        )
        return my_groups


class NotifyAdviser(generics.CreateAPIView):
    """Уведомлять адвайзера о том, что студент завершил регистрацию на дисциплины"""
    serializer_class = serializers.NotifyAdviserSerializer
    permission_classes = (
        IsAuthenticated,
        permissions.StudyPlanPermission,
    )

    def create(self, request, *args, **kwargs):
        study_plan_id = request.data.get('study_plan')
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

        self.check_object_permissions(request,
                                      study_plan)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'message': 'ok'
            },
            status=status.HTTP_200_OK
        )


class StudentAllDisciplineListView(generics.ListAPIView):
    """Получить список дисциплин студента
    Принимает: query_params: ?study_plan=<uid study_plan>
    """
    # &acad_period=<uid acad_period>
    permission_classes = (
        IsAuthenticated,
        permissions.StudyPlanPermission,
    )
    serializer_class = serializers.StudentDisciplineShortSerializer

    def list(self, request, *args, **kwargs):
        study_plan_id = request.query_params.get('study_plan')
        # acad_period_id = request.query_params.get('acad_period')

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

        acad_period_pks = org_models.StudentDiscipline.objects.filter(
            study_plan_id=study_plan_id,
            is_active=True,
        ).values('acad_period')

        acad_periods = org_models.AcadPeriod.objects.filter(pk__in=acad_period_pks)

        resp = []

        for acad_period in acad_periods:
            student_disciplines = org_models.StudentDiscipline.objects.filter(
                study_plan_id=study_plan_id,
                acad_period=acad_period,
                is_active=True,
            ).order_by('discipline')
            serializer = self.serializer_class(student_disciplines,
                                               many=True)
            item_key = acad_period.repr_name
            item = {
                item_key: serializer.data
            }
            resp.append(item)

        return Response(
            resp,
            status=status.HTTP_200_OK
        )


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
        IsAuthenticated,
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
            return Response(
                {
                    'message': 'not_authenticated'
                },
                status=status.HTTP_200_OK
            )

        serializer = self.serializer_class(instance=request.user.profile)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

