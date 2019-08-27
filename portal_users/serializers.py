from rest_framework import serializers
from . import models
from rest_framework_recaptcha.fields import ReCaptchaField
from django.contrib.auth.models import User
from common.exceptions import CustomException
from django.contrib.auth import password_validation
from cron_app.models import EmailTask


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
    )
    password = serializers.CharField(
        required=True,
    )
    # recaptcha = ReCaptchaField()


class ProfileDetailSerializer(serializers.ModelSerializer):
    userId = serializers.PrimaryKeyRelatedField(
        source='user',
        read_only=True,
    )
    middleName = serializers.CharField(
        max_length=100,
        source='middle_name',
        allow_blank=True,
    )
    firstName = serializers.CharField(
        max_length=100,
        source='first_name',
        required=True,
    )
    lastName = serializers.CharField(
        max_length=100,
        source='last_name',
        required=True,
    )

    class Meta:
        model = models.Profile
        fields = (
            'userId',
            'firstName',
            'lastName',
            'middleName',
        )


class PasswordChangeSerializer(serializers.ModelSerializer):
    oldPassword = serializers.CharField()
    passwordConfirm = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'id',
            'oldPassword',
            'password',
            'passwordConfirm',
        )

    def validate(self, data):
        user = self.context.get('request').user

        if not user.check_password(data['oldPassword']):
            raise CustomException(detail='wrong_old_password')

        if data['password'] != data['passwordConfirm']:
            raise CustomException(detail='password_mismatch')
        password_validation.validate_password(data['password'])
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        user.set_password(validated_data['password'])
        user.save()

        return user


class ForgetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResetPassword
        fields = (
            'id',
            'email',
        )

    def validate(self, data):
        if not User.objects.filter(email=data['email'],
                                   is_active=True).exists():
            raise CustomException(detail='not_fount')

        return data

    def create(self, validated_data):
        email = validated_data.get('email')

        user = User.objects.get(email=email,
                                is_active=True)
        reset = models.ResetPassword.objects.create(
            email=email,
            user=user
        )

        # Создаем задачу для крон
        EmailTask.objects.create(
            to=email,
            subject='Сброс пароля',
            message='{}'.format(reset.uuid)
        )

        return reset


class ResetPasswordSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['password2']:
            raise CustomException(detail='password_mismatch')

        password_validation.validate_password(data['password'])

        try:
            reset = models.ResetPassword.objects.get(uuid=data['uuid'])
        except models.ResetPassword.DoesNotExist:
            raise CustomException(detail='not_found')

        if reset.changed:
            raise CustomException(detail='expired')

        try:
            user = User.objects.get(email=reset.email)
        except User.DoesNotExist:
            raise CustomException(detail='not_found')

        if reset.user.id != user.id:
            raise CustomException(detail='not_found')

        return data

    def save(self, **kwargs):
        reset = models.ResetPassword.objects.get(uuid=self.validated_data['uuid'])
        user = reset.user
        user.set_password(self.validated_data['password'])
        user.save()
        reset.changed = True
        reset.save()

        return reset

