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
                            username=cd['username'].lower(),
                            password=cd['password'])
        if user is not None:
            profile_serializer = serializers.ProfileDetailSerializer(instance=user.profile)
            data = {
                'user': profile_serializer.data,
                'firstLogin': user.last_login is None
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
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                'message': 'ok'
            }
        )


class ForgetPasswordView(generics.CreateAPIView):
    """Забыли пароль"""
    permission_classes = ()
    authentication_classes = ()
    queryset = models.ResetPassword.objects.all()
    serializer_class = serializers.ForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                'message': 'ok'
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
                'message': 'ok'
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


class StudentDisciplineListView(generics.ListAPIView):  # TODO Создать  StudentDisciplineInfo ЕСЛИ НЕ СОЗДАН СО СТАТУСОМ "НЕ НАЧАТО"
    """Получить список дисциплин в текущем академическом периоде для регистрации"""
    serializer_class = serializers.StudentDisciplineSerializer

    def list(self, request, *args, **kwargs):
        profile = request.user.profile

        current_acad_period = "d922e730-2b90-4296-9802-1853020b0357"  # 1 trimestr  # TODO определить текущий Семестр или Триместр

        current_study_year = get_current_study_year()
        study_plans = org_models.StudyPlan.objects.filter(
            student=profile,
            study_period__end__gt=current_study_year.get('start'),
            is_active=True,
        )
        resp = []
        for study_plan in study_plans:
            student_disciplines = org_models.StudentDiscipline.objects.filter(
                study_plan=study_plan,
                acad_period_id=current_acad_period,
            )
            serializer = self.serializer_class(student_disciplines,
                                               many=True)
            item = {
                "study_plan_id": study_plan.pk,
                'speciality_name': study_plan.speciality.name,
                'active': False,
                'disciplines': serializer.data,
            }
            resp.append(item)

        return Response(
            resp,
            status=status.HTTP_200_OK
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
    """Уведомлять адвайзера о выборе преподов для всех дисциплин"""
    serializer_class = serializers.NotifyAdviserSerializer


# class StudentAllDisciplineListView(generics.ListAPIView):  # TODO  группировать по акам периоду
#     serializer_class = serializers.StudentDisciplineShortSerializer
#
#     def get_queryset(self):
#         pass

