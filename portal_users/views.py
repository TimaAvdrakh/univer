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


class StudentDisciplineListView(generics.ListAPIView):
    """Получить список дисциплин студента"""
    queryset = org_models.StudentDiscipline.objects.filter(is_active=True)
    serializer_class = serializers.StudentDisciplineSerializer

    def get_queryset(self):
        acad_period = self.request.query_params.get('acad_period')

        if acad_period:
            pass
        else:
            acad_period = "d922e730-2b90-4296-9802-1853020b0357"  # 1 trimestr

        queryset = self.queryset.filter(student=self.request.user.profile,
                                        acad_period_id=acad_period)
        return queryset


class StudyPlanDetailView(generics.RetrieveAPIView):
    """Получить мой учебный план"""
    queryset = org_models.StudyPlan.objects.filter(is_active=True)
    serializer_class = serializers.StudyPlanSerializer

    def get_object(self):
        obj = self.queryset.get(student=self.request.user.profile)
        return obj


class ChooseTeacherView(generics.UpdateAPIView):
    """Выбрать преподавателя"""
    permission_classes = (
        IsAuthenticated,
        permissions.StudentDisciplinePermission
    )
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
                                           instance=student_discipline)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "ok",
            },
            status=status.HTTP_200_OK
        )


class MyGroupDetailView(generics.ListAPIView):
    """Получить инфо о моих группах"""
    serializer_class = serializers.GroupDetailSerializer

    def get_queryset(self):
        request = self.request
        my_group_pks = org_models.StudyPlan.objects.filter(student=request.user.profile,
                                                           is_active=True).values('group')
        my_groups = org_models.Group.objects.filter(pk__in=my_group_pks)
        return my_groups
