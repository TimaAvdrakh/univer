from rest_framework import serializers
from . import models
from rest_framework_recaptcha.fields import ReCaptchaField
from django.contrib.auth.models import User
from common.exceptions import CustomException
from django.contrib.auth import password_validation
from cron_app.models import ResetPasswordUrlSendTask, CredentialsEmailTask, NotifyAdvisorTask
from common.utils import password_generator
from organizations import models as org_models
from portal.curr_settings import student_discipline_status, student_discipline_info_status, language_multilingual_id
from django.db.models import Q
from common import serializers as common_serializers
from uuid import uuid4


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
            'is_supervisor',
        )


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Interest
        list_serializer_class = common_serializers.FilteredListSerializer
        fields = (
            'uid',
            'name',
            'is_active',
        )


class AchievementSerializer(serializers.ModelSerializer):
    achievement_type = serializers.CharField()
    level = serializers.CharField()

    class Meta:
        model = models.Achievement
        list_serializer_class = common_serializers.FilteredListSerializer
        fields = (
            'uid',
            'achievement_type',
            'level',
            'content',
        )


class ProfileFullSerializer(serializers.ModelSerializer):
    """Используется для получения и редактирования профиля"""
    profileId = serializers.CharField(
        source='uid',
        read_only=True,
    )
    firstName = serializers.CharField(
        max_length=100,
        source='first_name',
        read_only=True,
    )
    lastName = serializers.CharField(
        max_length=100,
        source='last_name',
        read_only=True,
    )
    middleName = serializers.CharField(
        max_length=100,
        source='middle_name',
        read_only=True,
    )
    gender = serializers.CharField(
        read_only=True,
    )
    marital_status = serializers.CharField(
        read_only=True,
    )
    interests = InterestSerializer(
        many=True,
        required=False,
    )
    interests_for_del = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    achievements = AchievementSerializer(
        many=True,
        required=False,
    )
    achievements_for_del = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    identity_documents = common_serializers.IdentityDocumentSerializer(
        many=True,
        required=False,
    )
    educations = common_serializers.EducationSerializer(
        many=True,
        required=False,
    )
    nationality = serializers.CharField()
    citizenship = serializers.CharField()

    class Meta:
        model = models.Profile
        fields = (
            'profileId',
            'student_id',
            'firstName',
            'lastName',
            'middleName',
            'first_name_en',
            'last_name_en',
            'birth_date',
            'birth_place',
            'nationality',
            'citizenship',
            'gender',
            'marital_status',
            'address',
            'phone',
            'email',
            'skype',
            'avatar',
            'interests',
            'interests_for_del',
            'achievements',
            'achievements_for_del',
            'extra_data',
            'iin',
            'identity_documents',
            'educations',
        )
        read_only_fields = (
            'iin',
        )

    def update(self, instance, validated_data):
        instance.address = validated_data.get('address', instance.address)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.skype = validated_data.get('skype', instance.skype)
        instance.extra_data = validated_data.get('extra_data', instance.extra_data)
        instance.save()

        interests = validated_data.get('interests')
        for interest in interests:
            models.Interest.objects.get_or_create(
                profile=instance,
                name=interest['name'],
                is_active=True,
            )

        interests_for_del = validated_data.get('interests_for_del')
        models.Interest.objects.filter(pk__in=interests_for_del).update(is_active=False)

        achievements = validated_data.get('achievements')
        for achievement in achievements:
            models.Achievement.objects.get_or_create(
                profile=instance,
                level_id=achievement['level'],
                achievement_type_id=achievement['achievement_type'],
                content=achievement['content'],
                is_active=True,
            )

        achievements_for_del = validated_data.get('achievements_for_del')
        models.Achievement.objects.filter(pk__in=achievements_for_del).update(is_active=False)

        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance=instance)
        role = models.Role.objects.filter(profile=instance).first()
        is_employee = False
        if role.is_teacher or role.is_supervisor or role.is_org_admin:
            is_employee = True
            teacher = models.Teacher.objects.get(profile=request.user.profile)
            data['employee'] = TeacherSerializer(teacher).data
            teacher_positions = models.TeacherPosition.objects.filter(teacher=teacher,
                                                                      is_active=True)
            data['positions'] = TeacherPositionSerializer(teacher_positions,
                                                          many=True).data

        role_serializer = RoleSerializer(instance=role)
        data['role'] = role_serializer.data

        data['is_employee'] = is_employee

        if request.user.profile != instance:
            data['iin'] = ''

        if request.user.profile != instance:
            data['identity_documents'] = []

        return data


class ProfileDetailSerializer(serializers.ModelSerializer):
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
            raise CustomException(detail=3)  # wrong_old_password

        if data['password'] != data['passwordConfirm']:
            raise CustomException(detail=2)  # password_mismatch
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
            raise CustomException(detail=2)  # not_found

        return data

    def create(self, validated_data):
        request = self.context.get('request')
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
            lang_code=request.LANGUAGE_CODE,
        )

        return reset


class ResetPasswordSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['password2']:
            raise CustomException(detail=2)  # password_mismatch

        password_validation.validate_password(data['password'])

        try:
            reset = models.ResetPassword.objects.get(uuid=data['uuid'])
        except models.ResetPassword.DoesNotExist:
            raise CustomException(detail=3)  # not_found

        if reset.changed:
            raise CustomException(detail=4)  # expired

        try:
            user = User.objects.get(email=reset.email)
        except User.DoesNotExist:
            raise CustomException(detail=3)  # not_found

        if reset.user.id != user.id:
            raise CustomException(detail=3)  # not_found

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


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Language
        fields = (
            # 'uid',
            'name',
        )


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


class StudentDisciplineStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.StudentDisciplineStatus
        fields = (
            'name',
            'number',
        )


class StudentDisciplineSerializer(serializers.ModelSerializer):
    acad_period = serializers.CharField(read_only=True)
    discipline = serializers.CharField(read_only=True)
    load_type = serializers.CharField(read_only=True)
    teacher = ProfileShortSerializer()
    status = StudentDisciplineStatusSerializer()
    author = ProfileShortSerializer()
    language = serializers.CharField()

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            'acad_period',
            'discipline',
            'load_type',
            'hours',
            'status',
            'author',
            'teacher',
            'language',
        )
        read_only_fields = (
            'uid',
            'student',
            'study_plan',
            'hours',
            'language',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        teacher_disciplines, languages = self.__get_allowed_teachers(instance)
        teachers_serializer = TeacherDisciplineSerializer(instance=teacher_disciplines,
                                                          many=True)
        if languages:
            """Мультиязычная группа"""
            lang_serializer = LanguageSerializer(instance=languages,
                                                 many=True)
            data['languages'] = lang_serializer.data
        else:
            data['languages'] = []

        data['selection_teachers'] = teachers_serializer.data

        return data

    def __get_allowed_teachers(self, instance):
        lang = instance.study_plan.group.language
        if str(lang.uid) == language_multilingual_id:
            """Если группа мультиязычная, то отдаем преподы независимо от языка преподавания"""
            teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
                discipline=instance.discipline,
                load_type2=instance.load_type.load_type2
            )
            language_pks = org_models.TeacherDiscipline.objects.filter(
                discipline=instance.discipline,
                load_type2=instance.load_type.load_type2
            ).values('language').distinct('language')
            languages = org_models.Language.objects.filter(pk__in=language_pks)
        else:
            teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
                discipline=instance.discipline,
                language=lang,
                load_type2=instance.load_type.load_type2
            )
            languages = None

        return teacher_disciplines, languages


class EducationProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.EducationProgram
        fields = (
            'uid',
            'name',
            'code',
        )


class EducationProgramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.EducationProgramGroup
        fields = (
            'uid',
            'name',
            'code',
        )


class StudyPlanSerializer(serializers.ModelSerializer):
    study_period = serializers.CharField()
    group = serializers.CharField()
    speciality = serializers.CharField()
    faculty = serializers.CharField()
    cathedra = serializers.CharField()
    education_program = EducationProgramSerializer()
    education_type = serializers.CharField()
    preparation_level = serializers.CharField()
    study_form = serializers.CharField()
    on_base = serializers.CharField()
    education_base = serializers.CharField()
    active = serializers.BooleanField(
        default=False,  # Для удобства на фронте
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
            'education_base',
            'active',
            'current_course',
            'entry_date',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['is_multilang'] = False
        if str(instance.group.language.pk) == language_multilingual_id:
            data['is_multilang'] = True

        data['language'] = instance.group.language.name

        return data


class ChooseTeacherSerializer(serializers.ModelSerializer):
    """Студент выбирает препода или эдвайзер за студента"""
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
        instance.language = teacher_discipline.language

        if request.user.profile == instance.student:
            """Студент сам делает выбор"""
            instance.status_id = student_discipline_status['chosen']
        elif request.user.profile == instance.study_plan.advisor:
            """Эдвайзер делает выбор за студента"""
            instance.status_id = student_discipline_status['changed']

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
        if str(lang.uid) == language_multilingual_id:
            """Если группа мультиязычная, то отдаем преподы независимо от языка преподавания"""
            teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
                discipline=instance.discipline,
                load_type2=instance.load_type.load_type2
            )
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
            'language',
            'students',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        study_plans = org_models.StudyPlan.objects.filter(
            student=request.user.profile,
            group=instance,
            is_active=True,
        ).distinct('advisor')

        data['supervisors'] = []
        for study_plan in study_plans:
            advisor_serializer = ProfileDetailSerializer(study_plan.advisor)
            item = {
                'supervisor': advisor_serializer.data,
                'edu_program': study_plan.education_program.name,
                'edu_program_code': study_plan.education_program.code,
            }
            data['supervisors'].append(item)

        for student in data['students']:
            if student['profile']['profileId'] == data['headman']['profileId']:
                data['students'].remove(student)

        return data


class StudentDisciplineShortSerializer(serializers.ModelSerializer):
    """Используется для получения всех дисциплин студента во всех акад.периодах"""

    # acad_period = serializers.CharField(read_only=True)
    discipline = serializers.CharField(read_only=True)
    load_type = serializers.CharField(read_only=True)

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            # 'study_plan',
            # 'acad_period',
            'discipline',
            'load_type',
            'hours',
        )


class NotifyAdviserSerializer(serializers.Serializer):
    """Уведомлять адвайзера о том, что студент завершил регистрацию на дисциплины"""
    study_plan = serializers.PrimaryKeyRelatedField(
        queryset=org_models.StudyPlan.objects.filter(is_active=True),
    )
    acad_period = serializers.PrimaryKeyRelatedField(
        queryset=org_models.AcadPeriod.objects.filter(is_active=True),
    )

    def save(self, **kwargs):
        study_plan = self.validated_data.get('study_plan')
        acad_period = self.validated_data.get('acad_period')

        try:
            student_discipline_info = org_models.StudentDisciplineInfo.objects.get(
                study_plan=study_plan,
                acad_period=acad_period
            )
        except org_models.StudentDisciplineInfo.DoesNotExist:
            student_discipline_info = org_models.StudentDisciplineInfo.objects.create(
                student=study_plan.student,
                study_plan=study_plan,
                acad_period=acad_period,
                status_id=student_discipline_info_status["not_started"],
            )

        if str(student_discipline_info.status_id) == student_discipline_info_status['chosen']:
            """Все дисциплины выбраны для выбранного академ/периода"""
            # Создаем задачу для отправки уведомления
            NotifyAdvisorTask.objects.create(stud_discipline_info=student_discipline_info)
        else:
            raise CustomException(detail="not_all_chosen")


class ProfileContactEditSerializer(serializers.ModelSerializer):
    """Используется для редактирования контактных данных профиля"""
    profileId = serializers.CharField(
        source='uid',
        read_only=True,
    )

    class Meta:
        model = models.Profile
        fields = (
            'profileId',
            'address',
            'phone',
            'email',
            'skype',
            'extra_data',
        )

    def update(self, instance, validated_data):
        instance.address = validated_data.get('address', instance.address)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.skype = validated_data.get('skype', instance.skype)
        instance.extra_data = validated_data.get('extra_data', instance.extra_data)
        instance.save()

        return instance


class ProfileInterestsEditSerializer(serializers.ModelSerializer):
    """Используется для редактирования интереса"""
    profileId = serializers.CharField(
        source='uid',
        read_only=True,
    )
    interests = InterestSerializer(
        many=True,
        required=False,
    )
    interests_for_del = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )

    class Meta:
        model = models.Profile
        fields = (
            'profileId',
            'interests',
            'interests_for_del',
        )

    def update(self, instance, validated_data):
        interests = validated_data.get('interests')
        for interest in interests:
            models.Interest.objects.get_or_create(
                profile=instance,
                name=interest['name'],
                is_active=True,
            )

        interests_for_del = validated_data.get('interests_for_del')
        models.Interest.objects.filter(pk__in=interests_for_del).update(is_active=False)

        return instance


class ProfileAchievementsEditSerializer(serializers.ModelSerializer):
    """Используется для редактирования достижения"""
    profileId = serializers.CharField(
        source='uid',
        read_only=True,
    )
    achievements = AchievementSerializer(
        many=True,
        required=False,
    )
    achievements_for_del = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )

    class Meta:
        model = models.Profile
        fields = (
            'profileId',
            'achievements',
            'achievements_for_del',
        )

    def update(self, instance, validated_data):
        achievements = validated_data.get('achievements')
        for achievement in achievements:
            models.Achievement.objects.get_or_create(
                profile=instance,
                level_id=achievement['level'],
                achievement_type_id=achievement['achievement_type'],
                content=achievement['content'],
                is_active=True,
            )

        achievements_for_del = validated_data.get('achievements_for_del')
        models.Achievement.objects.filter(pk__in=achievements_for_del).update(is_active=False)

        return instance


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = (
            'uid',
            'avatar',
        )

    def create(self, validated_data):
        request = self.context.get('request')
        profile = request.user.profile

        image = validated_data['avatar']
        extension = image.name.split('.')[-1]
        image_name = '{}.{}'.format(str(uuid4()),
                                    extension)

        profile.avatar.save(image_name,
                            image,
                            save=True)
        return profile


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = (
            'academic_degree',
            'academic_rank',
            'work_experience_year',
            'work_experience_month',
        )


class TeacherPositionSerializer(serializers.ModelSerializer):
    position = serializers.CharField()
    cathedra = serializers.CharField()

    class Meta:
        model = models.TeacherPosition
        fields = (
            # 'teacher',
            'position',
            'cathedra',
            'is_main',
        )
