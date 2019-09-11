from rest_framework import serializers
from . import models
from rest_framework_recaptcha.fields import ReCaptchaField
from django.contrib.auth.models import User
from common.exceptions import CustomException
from django.contrib.auth import password_validation
from cron_app.models import ResetPasswordUrlSendTask, CredentialsEmailTask
from common.utils import password_generator
from organizations import models as org_models
from portal.curr_settings import student_discipline_status, student_discipline_info_status, language_multilingual_id
from django.db.models import Q


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
    )
    password = serializers.CharField(
        required=True,
    )
    # recaptcha = ReCaptchaField()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = (
            'is_student',
            'is_teacher',
            'is_org_admin',
        )


class ProfileDetailSerializer(serializers.ModelSerializer):
    profileId = serializers.CharField(
        source='uid',
    )
    # userId = serializers.PrimaryKeyRelatedField(
    #     source='user',
    #     read_only=True,
    # )
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
            'profileId',
            # 'userId',
            'firstName',
            'lastName',
            'middleName',
            'phone',
            'email',
            'avatar'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        role = models.Role.objects.filter(profile=instance).first()
        role_serializer = RoleSerializer(instance=role)
        data['role'] = role_serializer.data
        return data


class ProfileShortSerializer(serializers.ModelSerializer):
    profileId = serializers.CharField(
        source='uid',
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
            'profileId',
            'firstName',
            'lastName',
            'middleName',
            # 'avatar'
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


class TeacherDisciplineSerializer(serializers.ModelSerializer):
    teacher = ProfileShortSerializer()
    language = serializers.CharField()

    class Meta:
        model = org_models.TeacherDiscipline
        fields = (
            'uid',
            'teacher',
            'language',
        )


class StudentDisciplineSerializer(serializers.ModelSerializer):
    acad_period = serializers.CharField(read_only=True)
    discipline = serializers.CharField(read_only=True)
    load_type = serializers.CharField(read_only=True)
    teacher = ProfileShortSerializer()
    status = serializers.CharField()
    author = ProfileShortSerializer()

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            # 'student',
            # 'study_plan',
            'acad_period',
            'discipline',
            'load_type',
            'hours',
            'status',
            'author',
            'teacher',
        )
        read_only_fields = (
            'uid',
            'student',
            'study_plan',
            'hours',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        teacher_disciplines = self.__get_allowed_teachers(instance)
        teachers_serializer = TeacherDisciplineSerializer(instance=teacher_disciplines,
                                                          many=True)
        data['selection_teachers'] = teachers_serializer.data

        return data

    def __get_allowed_teachers(self, instance):
        lang = instance.study_plan.group.language
        if lang.uid == language_multilingual_id:
            """Если группа мультиязычная, то отдаем преподы независимо от языка преподавания"""
            teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
                discipline=instance.discipline,
                load_type2=instance.load_type.load_type2
            ).values('teacher').distinct('teacher')
        else:
            teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
                discipline=instance.discipline,
                language=lang,
                load_type2=instance.load_type.load_type2
            )

        return teacher_disciplines


class StudyPlanSerializer(serializers.ModelSerializer):
    study_period = serializers.CharField()
    group = serializers.CharField()
    speciality = serializers.CharField()
    faculty = serializers.CharField()
    cathedra = serializers.CharField()
    education_program = serializers.CharField()
    education_type = serializers.CharField()
    preparation_level = serializers.CharField()
    study_form = serializers.CharField()
    on_base = serializers.CharField()
    active = serializers.BooleanField(
        default=False,
    )

    class Meta:
        model = org_models.StudyPlan
        fields = (
            'uid',
            'student',
            'study_period',
            'group',
            'speciality',
            'faculty',
            'cathedra',
            'education_program',
            'education_type',
            'preparation_level',
            'study_form',
            'on_base',
            'active',
        )


class ChooseTeacherSerializer(serializers.ModelSerializer):
    """Выбирает препода студент"""
    teacher_discipline = serializers.PrimaryKeyRelatedField(
        queryset=org_models.TeacherDiscipline.objects.filter(is_active=True),
    )

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            'teacher_discipline',
        )

    def update(self, instance, validated_data):
        request = self.context.get('request')

        teacher_disciplines = self.__get_allowed_teachers(instance)
        teachers_pk = teacher_disciplines.values('teacher')
        teachers = models.Profile.objects.filter(pk__in=teachers_pk)

        teacher_discipline = validated_data.get('teacher_discipline')
        chosen_teacher = teacher_discipline.teacher

        if chosen_teacher not in teachers:
            raise CustomException(detail='teacher_not_allowed')

        instance.teacher = chosen_teacher
        instance.status_id = student_discipline_status['chosen']
        instance.author = request.user.profile
        instance.save()

        self.__check_is_all_disciplines_chosen(instance)
        return instance

    def __check_is_all_disciplines_chosen(self, instance):
        """Проверяет все дисциплины выбраны для текущего учебного плана и акамдемического плана"""
        study_plan = instance.study_plan
        acad_period = instance.acad_period

        try:
            student_discipline_info = org_models.StudentDisciplineInfo.objects.get(study_plan=study_plan,
                                                                                   acad_period=instance.acad_period)
        except org_models.StudentDisciplineInfo.DoesNotExist:
            student_discipline_info = org_models.StudentDisciplineInfo.objects.create(
                student=study_plan.student,
                study_plan=study_plan,
                acad_period=acad_period,
            )

        if org_models.StudentDiscipline.objects.filter(
                Q(status_id=student_discipline_status["not_chosen"]) | Q(
                    status_id=student_discipline_status["rejected"]),
                study_plan=study_plan,
                acad_period=acad_period,
                is_active=True,
        ).exists():
            """Если есть дисциплина где не выбран препод или отклонен"""
            student_discipline_info.status_id = student_discipline_info_status['choosing']
        else:
            student_discipline_info.status_id = student_discipline_info_status['chosen']
        student_discipline_info.save()

    def __get_allowed_teachers(self, instance):
        lang = instance.study_plan.group.language
        if lang.uid == language_multilingual_id:
            """Если группа мультиязычная, то отдаем преподы независимо от языка преподавания"""
            teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
                discipline=instance.discipline,
                load_type2=instance.load_type.load_type2
            ).values('teacher').distinct('teacher')
        else:
            teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
                discipline=instance.discipline,
                language=lang,
                load_type2=instance.load_type.load_type2
            )

        return teacher_disciplines


class StudentSerializer(serializers.ModelSerializer):
    profile = ProfileDetailSerializer()

    class Meta:
        model = org_models.Student
        fields = (
            'profile',
        )


class GroupDetailSerializer(serializers.ModelSerializer):
    headman = ProfileDetailSerializer()
    kurator = ProfileDetailSerializer()
    supervisor = ProfileDetailSerializer()
    students = StudentSerializer(many=True)
    active = serializers.BooleanField(
        default=False,
    )

    class Meta:
        model = org_models.Group
        fields = (
            'name',
            'active',
            'headman',
            'kurator',
            'supervisor',
            'language',
            'students',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        for student in data['students']:
            if student['profile']['profileId'] == str(request.user.profile.pk):
                data['students'].remove(student)

        return data


class StudentDisciplineShortSerializer(serializers.ModelSerializer):
    """Используется для получения всех дисциплин студента во всех акад.периодах"""

    acad_period = serializers.CharField(read_only=True)
    discipline = serializers.CharField(read_only=True)
    load_type = serializers.CharField(read_only=True)

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            'student',
            'study_plan',
            'acad_period',
            'discipline',
            'load_type',
            'hours',
        )


class NotifyAdviserSerializer(serializers.Serializer):
    """Уведомлять адвайзера о выборе преподов для всех дисциплин"""

    study_plan = serializers.PrimaryKeyRelatedField(
        queryset=org_models.StudyPlan.objects.filter(is_active=True),
    )

    def save(self, **kwargs):
        study_plan = self.validated_data.get('study_plan')
        current_acad_period = "d922e730-2b90-4296-9802-1853020b0357"

        try:
            student_discipline_info = org_models.StudentDisciplineInfo.objects.get(
                study_plan=study_plan,
                acad_period=current_acad_period
            )
        except org_models.StudentDisciplineInfo.DoesNotExist:
            student_discipline_info = org_models.StudentDisciplineInfo.objects.create(
                student=study_plan.student,
                study_plan=study_plan,
                acad_period=current_acad_period,
            )

        if str(student_discipline_info.status_id) == student_discipline_info_status['chosen']:
            """Все дисциплины выбраны для текущего академ/периода"""
            print('Ok')
            # TODO уведомляем эдвайзера о том, что студент выбрал все диспциплины для текущего семестра
        else:
            raise CustomException(detail="not_all_chosen")
