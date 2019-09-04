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
    queryset = org_models.StudentDiscipline.objects.filter(is_active=True)
    serializer_class = serializers.StudentDisciplineSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(student=self.request.user)
        return queryset
        # 1
