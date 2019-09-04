from rest_framework import serializers
from . import models
from rest_framework_recaptcha.fields import ReCaptchaField
from django.contrib.auth.models import User
from common.exceptions import CustomException
from django.contrib.auth import password_validation
from cron_app.models import ResetPasswordUrlSendTask, CredentialsEmailTask
from common.utils import password_generator
from organizations import models as org_models


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
            'uid',
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
            'uid',
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
        ResetPasswordUrlSendTask.objects.create(
            reset_password=reset,
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


class UserCreateSerializer(serializers.ModelSerializer):
    # org_token = serializers.CharField(
    #     required=True,
    #     help_text='Токен организации для авторизации из 1С',
    # )
    uid = serializers.UUIDField(
        required=True,
        help_text='uuid для профиля из 1С'
    )
    middle_name = serializers.CharField(
        required=True,
    )
    first_name_en = serializers.CharField(
        required=True,
    )
    last_name_en = serializers.CharField(
        required=True,
    )
    birth_date = serializers.DateField(
        required=True,
    )
    birth_place = serializers.CharField(
        required=True,
    )
    nationality = serializers.CharField(
        required=True,
    )
    citizenship = serializers.CharField(
        required=True,
    )
    gender = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=models.Gender.objects.filter(is_active=True),
    )
    marital_status = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=models.MaritalStatus.objects.filter(is_active=True)
    )
    iin = serializers.CharField(
        required=True,
    )
    address = serializers.CharField(
        required=True,
    )
    phone = serializers.CharField(
        required=True,
    )
    email = serializers.EmailField(
        required=True,
    )
    skype = serializers.CharField(
        required=True,
    )
    entry_date = serializers.DateField(
        required=True,
    )
    study_form = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=org_models.StudyForm.objects.filter(is_active=True),
    )

    class Meta:
        model = models.Profile
        fields = (
            'uid',
            # 'org_token',
            'first_name',
            'last_name',
            'middle_name',
            'first_name_en',
            'last_name_en',
            'birth_date',
            'birth_place',
            'nationality',
            'citizenship',
            'gender',
            'marital_status',
            'iin',
            'address',
            'phone',
            'email',
            'skype',
            # 'interests',
            'entry_date',
            'study_form',
        )

    def create(self, validated_data):
        password = password_generator(size=8)

        user = User.objects.create(
            username=validated_data['iin'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(password)
        user.save()

        profile = models.Profile.objects.create(
            user=user,
            **validated_data
        )

        CredentialsEmailTask.objects.create(
            to=user.email,
            username=user.username,
            password=password
        )

        return profile


class StudentDisciplineSerializer(serializers.ModelSerializer):
    acad_period = serializers.CharField()
    discipline = serializers.CharField()
    load_type = serializers.CharField()
    teacher = ProfileDetailSerializer()

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'student',
            'study_plan',
            'acad_period',
            'discipline',
            'load_type',
            'hours',
            'teacher',
        )
