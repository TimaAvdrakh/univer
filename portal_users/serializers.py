from rest_framework import serializers
from . import models
from django.conf import settings
from django.contrib.auth.models import User
from common.exceptions import CustomException
from django.contrib.auth import password_validation
from cron_app.models import (
    CredentialsEmailTask,
    NotifyAdvisorTask,
)
from common.utils import password_generator
from organizations import models as org_models
from portal.curr_settings import (
    student_discipline_status,
    student_discipline_info_status,
    language_multilingual_id,
    not_choosing_load_types2,
    current_site
)
from django.db.models import Q
from common import serializers as common_serializers
from uuid import uuid4
from portal.curr_settings import current_site
from advisors.models import AdvisorCheck
from validate_email import validate_email
from datetime import date
from common import models as common_models
from django.utils.translation import ugettext as _
from mail.models import EmailTemplate


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True,)
    password = serializers.CharField(required=True,)
    # recaptcha = ReCaptchaField()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = (
            "is_student",
            "is_teacher",
            "is_org_admin",
            "is_supervisor",
            "is_applicant",
            "is_mod",
        )


class InterestSerializer(serializers.ModelSerializer):
    content = serializers.CharField(source="name",)

    class Meta:
        model = models.Interest
        list_serializer_class = common_serializers.FilteredListSerializer
        fields = (
            "uid",
            "content",
            "is_active",
        )


class InformationUsersCanSeeSerializer(serializers.ModelSerializer):
    """
    Список полей который могут видеть другие пользователи
    """

    class Meta:
        model = models.InfoShowPermission
        fields = (
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
            'interests',
            'extra_data',
            'identity_documents',
            'educations',
            'iin',
        )



class AchievementSerializer(serializers.ModelSerializer):
    achievement_type = serializers.CharField()
    level = serializers.CharField()

    class Meta:
        model = models.Achievement
        list_serializer_class = common_serializers.FilteredListSerializer
        fields = (
            "uid",
            "achievement_type",
            "level",
            "content",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        if data['achievement_type']:
            data['achievement_type_name'] = data['achievement_type']['name']
            data['level_name'] = data['level'].get('name')
        return data


class AchievementFullSerializer(serializers.ModelSerializer):
    achievement_type = common_serializers.AchievementTypeSerializer()
    level = common_serializers.LevelSerializer()

    class Meta:
        model = models.Achievement
        list_serializer_class = common_serializers.FilteredListSerializer
        fields = (
            "uid",
            "achievement_type",
            "level",
            "content",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        if data['achievement_type']:
            data['achievement_type_name'] = data['achievement_type']['name']
            data['level_name'] = data['level'].get('name')
        return data


class ProfileFullSerializer(serializers.ModelSerializer):
    """Используется для получения и редактирования профиля"""

    profileId = serializers.CharField(source="uid", read_only=True,)
    firstName = serializers.CharField(
        max_length=100, source="first_name", read_only=True,
    )
    lastName = serializers.CharField(
        max_length=100, source="last_name", read_only=True,
    )
    middleName = serializers.CharField(
        max_length=100, source="middle_name", read_only=True,
    )

    class Meta:
        model = models.Profile
        fields = (
            "profileId",
            "student_id",
            "firstName",
            "lastName",
            "middleName",
            "avatar",

        )
        read_only_fields = ("iin",)

    def update(self, instance, validated_data):
        instance.address = validated_data.get("address", instance.address)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.email = validated_data.get("email", instance.email)
        instance.skype = validated_data.get("skype", instance.skype)
        instance.extra_data = validated_data.get("extra_data", instance.extra_data)
        instance.notify_me_from_email = validated_data.get("notify_me_from_email", instance.notify_me_from_email)
        instance.save()

        interests = validated_data.get("interests")
        for interest in interests:
            models.Interest.objects.get_or_create(
                profile=instance, name=interest["name"], is_active=True,
            )

        interests_for_del = validated_data.get("interests_for_del")
        models.Interest.objects.filter(pk__in=interests_for_del).update(is_active=False)

        achievements = validated_data.get("achievements")
        for achievement in achievements:
            models.Achievement.objects.get_or_create(
                profile=instance,
                level_id=achievement["level"],
                achievement_type_id=achievement["achievement_type"],
                content=achievement["content"],
                is_active=True,
            )

        achievements_for_del = validated_data.get("achievements_for_del")
        models.Achievement.objects.filter(pk__in=achievements_for_del).update(
            is_active=False
        )

        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        data = super().to_representation(instance=instance)

        role = models.Role.objects.filter(profile=instance).first()
        is_employee = False

        if role.is_teacher or role.is_supervisor or role.is_org_admin:
            is_employee = True
            teacher = models.Teacher.objects.get(profile=instance)
            # data['employee'] = TeacherSerializer(teacher).data
            data.update(TeacherSerializer(teacher).data)
            teacher_positions = models.TeacherPosition.objects.filter(profile=instance,
                                                                      is_active=True)

            data['positions'] = TeacherPositionSerializer(teacher_positions,
                                                          many=True).data
        role_serializer = RoleSerializer(instance=role)
        data["role"] = role_serializer.data

        data["is_employee"] = is_employee

        fields_to_show = models.InfoShowPermission.objects.get_or_create(profile=instance)

        fields = InformationUsersCanSeeSerializer(fields_to_show, many=True).data[
            0 if fields_to_show[0] else 1
        ]
        fields_serializer = FieldsToShowSerializer(instance=instance, many=True).child.data
        if request.user.profile != instance:
            for field in fields:
                if fields[field]:
                    data[field] = fields_serializer[field]
        else:
            for field in fields_serializer:
                data[field] = fields_serializer[field]
            data['fields_to_show'] = InformationUsersCanSeeSerializer(fields_to_show,
                                                                      many=True).data
        return data


class FieldsToShowSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(read_only=True, )
    marital_status = serializers.CharField(read_only=True,)
    interests = InterestSerializer(many=True, required=False,)
    interests_for_del = serializers.ListField(
        child=serializers.CharField(), required=False,
    )
    achievements = AchievementFullSerializer(many=True, required=False,)
    achievements_for_del = serializers.ListField(
        child=serializers.CharField(), required=False,
    )
    identity_documents = common_serializers.IdentityDocumentSerializer(
        many=True, required=False,
    )
    educations = common_serializers.EducationSerializer(many=True, required=False,)
    nationality = serializers.CharField()
    citizenship = serializers.CharField()

    class Meta:
        model = models.Profile
        fields = (
            "first_name_en",
            "last_name_en",
            "birth_date",
            "birth_place",
            "nationality",
            "citizenship",
            "gender",
            "marital_status",
            "address",
            "phone",
            "email",
            "skype",
            "interests",
            "interests_for_del",
            "achievements",
            "achievements_for_del",
            "extra_data",
            "iin",
            "identity_documents",
            "educations",
            "notify_me_from_email",
        )


class ProfileDetailSerializer(serializers.ModelSerializer):
    """С префиксом домена в поле аватар"""

    profileId = serializers.CharField(source="uid",)
    middleName = serializers.CharField(
        max_length=100, source="middle_name", allow_blank=True,
    )
    firstName = serializers.CharField(
        max_length=100, source="first_name", required=True,
    )
    lastName = serializers.CharField(max_length=100, source="last_name", required=True,)

    class Meta:
        model = models.Profile
        fields = (
            "profileId",
            "firstName",
            "lastName",
            "middleName",
            "phone",
            "email",
            "avatar",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        role = models.Role.objects.filter(profile=instance).first()
        role_serializer = RoleSerializer(instance=role)
        data["role"] = role_serializer.data
        data['is_mod_can_edit'] = role.is_mod_can_edit

        if data["avatar"] is not None:
            data["avatar"] = current_site + data["avatar"]
        else:
            data['avatar'] = None
        return data


class ProfileSerializer(serializers.ModelSerializer):
    """Без префикс домена в поле аватар"""

    profileId = serializers.CharField(source="uid",)
    middleName = serializers.CharField(
        max_length=100, source="middle_name", allow_blank=True,
    )
    firstName = serializers.CharField(
        max_length=100, source="first_name", required=True,
    )
    lastName = serializers.CharField(max_length=100, source="last_name", required=True,)

    class Meta:
        model = models.Profile
        fields = (
            "profileId",
            "firstName",
            "lastName",
            "middleName",
            "phone",
            "email",
            "avatar",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        role = models.Role.objects.filter(profile=instance).first()
        role_serializer = RoleSerializer(instance=role)
        data["role"] = role_serializer.data

        return data


class ProfileLiteSerializer(serializers.ModelSerializer):
    # name = serializers.SerializerMethodField()

    # def get_name(self, profile: models.Profile):
    #     return profile.full_name

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = models.Profile
        fields = ['uid', 'full_name']


class ProfileShortSerializer(serializers.ModelSerializer):
    profileId = serializers.CharField(source="uid",)
    middleName = serializers.CharField(
        max_length=100, source="middle_name", allow_blank=True,
    )
    firstName = serializers.CharField(
        max_length=100, source="first_name", required=True,
    )
    lastName = serializers.CharField(max_length=100, source="last_name", required=True,)

    class Meta:
        model = models.Profile
        fields = (
            "profileId",
            "firstName",
            "lastName",
            "middleName",
        )


class PasswordChangeSerializer(serializers.ModelSerializer):
    oldPassword = serializers.CharField()
    passwordConfirm = serializers.CharField()

    class Meta:
        model = User
        fields = (
            "id",
            "oldPassword",
            "password",
            "passwordConfirm",
        )

    def validate(self, data):
        user = self.context.get("request").user

        if not user.check_password(data["oldPassword"]):
            raise CustomException(detail=3)  # wrong_old_password

        if data["password"] != data["passwordConfirm"]:
            raise CustomException(detail=2)  # password_mismatch
        password_validation.validate_password(data["password"])
        return data

    def create(self, validated_data):
        user = self.context.get("request").user
        user.set_password(validated_data["password"])
        user.save()

        user.profile.password_changed = True
        user.profile.save()

        return user


class ForgetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResetPassword
        fields = (
            "uid",
            "username",
        )

    def validate(self, data):
        if not User.objects.filter(username=data["username"], is_active=True).exists():
            raise CustomException(detail=2)  # not_found

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        username = validated_data.get("username")

        user = User.objects.get(username=username, is_active=True)
        email = user.email
        if len(email) == 0 or not validate_email(email):
            raise CustomException(detail=3)  # has_not_email_or_invalid_email

        reset = models.ResetPassword.objects.create(
            username=username, user=user, email=email,
        )
        EmailTemplate.put_in_cron_queue(
            EmailTemplate.PASS_RESET,
            email,
            **{'site': current_site, 'lang': 'ru', 'uid': reset.pk}
        )
        return reset


class ResetPasswordSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise CustomException(detail=2)  # password_mismatch

        password_validation.validate_password(data["password"])

        try:
            reset = models.ResetPassword.objects.get(pk=data["uuid"])
        except models.ResetPassword.DoesNotExist:
            raise CustomException(detail=3)  # not_found

        if reset.changed:
            raise CustomException(detail=4)  # expired

        try:
            user = User.objects.get(username=reset.username)
        except User.DoesNotExist:
            raise CustomException(detail=3)  # not_found

        if reset.user.id != user.id:
            raise CustomException(detail=3)  # not_found

        return data

    def save(self, **kwargs):
        reset = models.ResetPassword.objects.get(pk=self.validated_data["uuid"])
        user = reset.user
        user.set_password(self.validated_data["password"])
        user.save()
        reset.changed = True
        reset.save()

        return reset


class UserCreateSerializer(serializers.ModelSerializer):
    # org_token = serializers.CharField(
    #     required=True,
    #     help_text='Токен организации для авторизации из 1С',
    # )
    uid = serializers.UUIDField(required=True, help_text="uuid для профиля из 1С")
    middle_name = serializers.CharField(required=True,)
    first_name_en = serializers.CharField(required=True,)
    last_name_en = serializers.CharField(required=True,)
    birth_date = serializers.DateField(required=True,)
    birth_place = serializers.CharField(required=True,)
    nationality = serializers.CharField(required=True,)
    citizenship = serializers.CharField(required=True,)
    gender = serializers.PrimaryKeyRelatedField(
        required=True, queryset=models.Gender.objects.filter(is_active=True),
    )
    marital_status = serializers.PrimaryKeyRelatedField(
        required=True, queryset=models.MaritalStatus.objects.filter(is_active=True)
    )
    iin = serializers.CharField(required=True,)
    address = serializers.CharField(required=True,)
    phone = serializers.CharField(required=True,)
    email = serializers.EmailField(required=True,)
    skype = serializers.CharField(required=True,)
    study_form = serializers.PrimaryKeyRelatedField(
        required=True, queryset=org_models.StudyForm.objects.filter(is_active=True),
    )

    class Meta:
        model = models.Profile
        fields = (
            "uid",
            # 'org_token',
            "first_name",
            "last_name",
            "middle_name",
            "first_name_en",
            "last_name_en",
            "birth_date",
            "birth_place",
            "nationality",
            "citizenship",
            "gender",
            "marital_status",
            "iin",
            "address",
            "phone",
            "email",
            "skype",
            "study_form",
        )

    def create(self, validated_data):
        password = password_generator(size=8)

        user = User.objects.create(
            username=validated_data["iin"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(password)
        user.save()

        profile = models.Profile.objects.create(user=user, **validated_data)

        CredentialsEmailTask.objects.create(
            to=user.email, username=user.username, password=password
        )

        return profile


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Language
        fields = (
            'uid',
            "name",
        )


class TeacherDisciplineSerializer(serializers.ModelSerializer):
    teacher = ProfileShortSerializer()
    language = serializers.CharField()

    class Meta:
        model = org_models.TeacherDiscipline
        fields = (
            "uid",
            "teacher",
            "language",
        )


class StudentDisciplineStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.StudentDisciplineStatus
        fields = (
            "name",
            "number",
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
            "uid",
            "acad_period",
            "discipline",
            "load_type",
            "hours",
            "status",
            "author",
            "teacher",
            "language",
        )
        read_only_fields = (
            "uid",
            "student",
            "study_plan",
            "hours",
            "language",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        teacher_disciplines, languages = self.__get_allowed_teachers(instance)
        teachers_serializer = TeacherDisciplineSerializer(
            instance=teacher_disciplines, many=True
        )
        if languages:
            lang_serializer = LanguageSerializer(instance=languages, many=True)
            data["languages"] = lang_serializer.data
        else:
            data["languages"] = []
        data['selection_teachers'] = teachers_serializer.data
        data['ruled_out'] = False

        return data

    def __get_allowed_teachers(self, instance):
        study_year_id = self.context.get('study_year_id')

        teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
            discipline=instance.discipline,
            load_type2=instance.load_type.load_type2,
            is_active=True,
        )

        if study_year_id:
            teacher_disciplines = teacher_disciplines.filter(
                study_period_id=study_year_id,
            )
        language_pks = teacher_disciplines.values('language').distinct('language')
        teacher_disciplines = teacher_disciplines.order_by('teacher__last_name')

        languages = org_models.Language.objects.filter(pk__in=language_pks)

        return teacher_disciplines, languages


class StudentDisciplineListSerializer(serializers.ModelSerializer):
    """Используется для списка дисциплин в Регистрации на дисциплины"""

    discipline = serializers.CharField(read_only=True)

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            'discipline',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['credit'] = instance.credit
        except:
            pass

        sds = org_models.StudentDiscipline.objects.filter(
            student=instance.student,
            discipline=instance.discipline,
            study_plan=instance.study_plan,
            study_year=instance.study_year,
            acad_period=instance.acad_period,
        ).exclude(load_type__load_type2__in=not_choosing_load_types2).order_by('discipline')

        serializer = StudentDisciplineCopySerializer(instance=sds, many=True)
        data['load_types'] = serializer.data
        data['hide'] = False
        data['loader'] = False

        return data


class StudentDisciplineCopySerializer(serializers.ModelSerializer):
    acad_period = serializers.CharField(read_only=True)
    # discipline = serializers.CharField(read_only=True)
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
            # 'discipline',
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
            lang_serializer = LanguageSerializer(instance=languages,
                                                 many=True)
            data['languages'] = lang_serializer.data
        else:
            data['languages'] = []

        data['selection_teachers'] = teachers_serializer.data
        data['ruled_out'] = False

        # teacher_data = data['teacher']
        # org_models.TeacherDiscipline.objects.filter(
        #     teacher_id=teacher_data['profileId'],
        #
        # )
        # data['teacher'] = {
        #     'uid': '',
        #     'teacher': teacher_data,
        #     'language': data['language'],
        # }
        status_data = data['status']
        data['status'] = status_data['number']

        data['listStatus'] = {}
        statuses = org_models.StudentDisciplineStatus.objects.filter(is_active=True)
        for item in statuses:
            if item.number == 5:
                author = data['author']
                if author:
                    author_name = '{} {} {}'.format(author['lastName'],
                                                    author['firstName'],
                                                    author['middleName'])
                else:
                    author_name = ''
                data['listStatus'][item.number] = author_name
            else:
                data['listStatus'][item.number] = item.name

        return data

    def __get_allowed_teachers(self, instance):
        study_year_id = self.context.get("study_year_id")

        teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
            discipline=instance.discipline,
            load_type2=instance.load_type.load_type2,
            is_active=True,
        )

        if study_year_id:
            teacher_disciplines = teacher_disciplines.filter(
                study_period_id=study_year_id,
            )
        language_pks = teacher_disciplines.values("language").distinct("language")
        teacher_disciplines = teacher_disciplines.order_by("teacher__last_name")

        languages = org_models.Language.objects.filter(pk__in=language_pks)

        return teacher_disciplines, languages


class EducationProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.EducationProgram
        fields = (
            "uid",
            "name",
            "code",
        )


class EducationProgramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.EducationProgramGroup
        fields = (
            "uid",
            "name",
            "code",
        )


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Speciality
        fields = (
            "uid",
            "name",
            "code"
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
    active = serializers.BooleanField(default=False,)  # Для удобства на фронте

    class Meta:
        model = org_models.StudyPlan
        fields = (
            "uid",
            "uid_1c",
            "student",
            "study_period",
            "group",
            "speciality",
            "faculty",
            "cathedra",
            "education_program",
            "education_type",
            "preparation_level",
            "study_form",
            "on_base",
            "education_base",
            "active",
            "current_course",
            "entry_date",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        speciality_pk = org_models.Speciality.objects.filter(uid=instance.speciality.uid)
        data["speciality_with_code"] = SpecialitySerializer(instance=speciality_pk, many=True).data[0]
        data["is_multilang"] = False
        if str(instance.group.language.pk) == language_multilingual_id:
            data["is_multilang"] = True

        data["language"] = instance.group.language.name

        return data


class ChooseTeacherSerializer(serializers.ModelSerializer):
    """Студент выбирает препода или эдвайзер за студента"""

    teacher_discipline = serializers.PrimaryKeyRelatedField(
        queryset=org_models.TeacherDiscipline.objects.filter(is_active=True),
        allow_null=True,
    )

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            "uid",
            "teacher_discipline",
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")
        teacher_discipline = validated_data.get("teacher_discipline")
        if teacher_discipline is None:
            """Выбор отменен"""
            instance.teacher = None
            instance.language = None
            instance.status_id = student_discipline_status['not_chosen']
        else:
            teacher_disciplines = self.__get_allowed_teachers(instance)
            teachers_pk = teacher_disciplines.values("teacher")
            teachers = models.Profile.objects.filter(pk__in=teachers_pk)

            chosen_teacher = teacher_discipline.teacher

            if chosen_teacher not in teachers:
                raise CustomException(detail="teacher_not_allowed")

            instance.teacher = chosen_teacher
            instance.language = teacher_discipline.language

            if request.user.profile == instance.student:
                """Студент сам делает выбор"""
                instance.status_id = student_discipline_status["chosen"]
            elif request.user.profile == instance.study_plan.advisor:
                """Эдвайзер делает выбор за студента"""
                instance.status_id = student_discipline_status["changed"]
                AdvisorCheck.objects.create(
                    study_plan=instance.study_plan,
                    acad_period=instance.acad_period,
                    status=5,  # Изменено
                )

        instance.author = request.user.profile
        instance.save()

        self.__check_is_all_disciplines_chosen(instance)
        return instance

    def __check_is_all_disciplines_chosen(self, instance):
        """Проверяет все дисциплины выбраны для текущего учебного плана и акамдемического плана"""
        study_plan = instance.study_plan
        acad_period = instance.acad_period

        try:
            student_discipline_info = org_models.StudentDisciplineInfo.objects.get(
                study_plan=study_plan, acad_period=instance.acad_period
            )
        except org_models.StudentDisciplineInfo.DoesNotExist:
            student_discipline_info = org_models.StudentDisciplineInfo.objects.create(
                student=study_plan.student,
                study_plan=study_plan,
                acad_period=acad_period,
            )

        if org_models.StudentDiscipline.objects.filter(
            Q(status_id=student_discipline_status["not_chosen"])
            | Q(status_id=student_discipline_status["rejected"]),
            study_plan=study_plan,
            acad_period=acad_period,
            is_active=True,
        ).exists():
            """Если есть дисциплина где не выбран препод или отклонен"""
            student_discipline_info.status_id = student_discipline_info_status[
                "choosing"
            ]
        else:
            student_discipline_info.status_id = student_discipline_info_status["chosen"]
        student_discipline_info.save()

    def __get_allowed_teachers(self, instance):
        # lang = instance.study_plan.group.language

        # if str(lang.uid) == language_multilingual_id:
        """Если группа мультиязычная, то отдаем преподы независимо от языка преподавания"""

        teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
            discipline=instance.discipline,
            load_type2=instance.load_type.load_type2,
            is_active=True,
        )
        # else:
        #     teacher_disciplines = org_models.TeacherDiscipline.objects.filter(
        #         discipline=instance.discipline,
        #         language=lang,
        #         load_type2=instance.load_type.load_type2
        #     )

        return teacher_disciplines


# class StudentSerializer(serializers.Serializer):
#     profile = ProfileDetailSerializer()
#
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#
#         if data['profile']['avatar']:
#             data['profile']['avatar'] = current_site + data['profile']['avatar']
#
#         return data


class GroupDetailSerializer(serializers.ModelSerializer):
    headman = ProfileSerializer()
    kurator = ProfileSerializer()
    active = serializers.BooleanField(default=False,)

    class Meta:
        model = org_models.Group
        fields = (
            "name",
            "active",
            "headman",
            "kurator",
            "language",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        study_plans = org_models.StudyPlan.objects.filter(
            student=request.user.profile, group=instance, is_active=True,
        ).distinct("advisor")

        data["supervisors"] = []
        for study_plan in study_plans:
            advisor_serializer = ProfileDetailSerializer(study_plan.advisor)
            advisor_data = advisor_serializer.data

            item = advisor_data
            item["edu_program"] = study_plan.education_program.name
            item["edu_program_code"] = study_plan.education_program.code

            data["supervisors"].append(item)

        student_pks = org_models.StudyPlan.objects.filter(group=instance).values(
            "student"
        )
        if data["headman"] is not None:
            student_pks = student_pks.exclude(student=data["headman"]["profileId"])

        students = models.Profile.objects.filter(pk__in=student_pks, is_active=True)
        serializer = ProfileDetailSerializer(students, many=True)
        data["students"] = serializer.data

        return data


class StudentDisciplineShortSerializer2(serializers.ModelSerializer):
    """Используется для получения всех дисциплин студента во всех акад.периодах"""

    # acad_period = serializers.CharField(read_only=True)
    discipline = serializers.CharField(read_only=True)
    language = serializers.CharField(read_only=True)
    teacher = serializers.CharField(read_only=True)
    load_type = serializers.CharField(read_only=True)

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            # 'study_plan',
            # 'acad_period',
            'discipline',
            'language',
            'teacher',
            'load_type',
            'control_form',
            'credit_obj',
            'hours',
        )


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
            'credit_obj',
            'hours',
        )


class StudentDisciplineShortSerializer(serializers.ModelSerializer):
    """Используется для получения всех дисциплин студента во всех акад.периодах"""

    # acad_period = serializers.CharField(read_only=True)
    discipline = serializers.CharField(read_only=True)
    load_type = serializers.CharField(read_only=True)

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            "uid",
            # 'study_plan',
            # 'acad_period',
            'discipline',
            # 'control_form',
            'credit_obj',
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
        required=False,
    )
    status = serializers.BooleanField(default=False)

    def save(self, **kwargs):
        study_plan = self.validated_data.get('study_plan')
        acad_period = self.validated_data.get('acad_period')
        status = self.validated_data.get('status')
        self.validated_data.pop('status')


        if acad_period:
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

            if str(student_discipline_info.status_id) == student_discipline_info_status['chosen'] or status:
                """Все дисциплины выбраны для выбранного академ/периода"""
                # Создаем задачу для отправки уведомления
                if not status:
                    NotifyAdvisorTask.objects.create(stud_discipline_info=student_discipline_info)
            else:
                raise CustomException(detail="not_all_chosen")
        else:
            """
            Если акад период не передал, 
            то из правил берем доступыне акад периоды для регистрации
            """
            current_course = study_plan.current_course
            if current_course is None:
                raise CustomException(detail="not_actual_study_plan")

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
            for acad_period in acad_periods:
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

                if str(student_discipline_info.status_id) == student_discipline_info_status['chosen'] or status:
                    """Все дисциплины выбраны для выбранного академ/периода"""
                    # Создаем задачу для отправки уведомления
                    if not status:
                        NotifyAdvisorTask.objects.create(stud_discipline_info=student_discipline_info)
                else:
                    raise CustomException(detail="not_all_chosen")


class ProfileContactEditSerializer(serializers.ModelSerializer):
    """Используется для редактирования контактных данных профиля"""

    profileId = serializers.CharField(source="uid", read_only=True,)

    class Meta:
        model = models.Profile
        fields = (
            "profileId",
            "address",
            "phone",
            "email",
            "skype",
            "extra_data",
            "notify_me_from_email",
        )

    def update(self, instance, validated_data):
        instance.address = validated_data.get("address", instance.address)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.email = validated_data.get("email", instance.email)
        instance.skype = validated_data.get("skype", instance.skype)
        instance.extra_data = validated_data.get("extra_data", instance.extra_data)
        instance.notify_me_from_email = validated_data.get("notify_me_from_email", instance.notify_me_from_email)
        instance.save()

        return instance


class ProfileInterestsEditSerializer(serializers.ModelSerializer):
    """Используется для редактирования интереса"""

    profileId = serializers.CharField(source="uid", read_only=True,)
    interests = InterestSerializer(many=True, required=False,)
    interests_for_del = serializers.ListField(
        child=serializers.CharField(), required=False,
    )

    class Meta:
        model = models.Profile
        fields = (
            "profileId",
            "interests",
            "interests_for_del",
        )

    def update(self, instance, validated_data):
        interests = validated_data.get("interests")
        for interest in interests:
            models.Interest.objects.get_or_create(
                profile=instance, name=interest["name"], is_active=True,
            )

        interests_for_del = validated_data.get("interests_for_del")
        models.Interest.objects.filter(pk__in=interests_for_del).update(is_active=False)

        return instance


class ProfileAchievementsEditSerializer(serializers.ModelSerializer):
    """Используется для редактирования достижения"""

    profileId = serializers.CharField(source="uid", read_only=True,)
    achievements = AchievementSerializer(many=True, required=False,)
    achievements_for_del = serializers.ListField(
        child=serializers.CharField(), required=False,
    )

    class Meta:
        model = models.Profile
        fields = (
            "profileId",
            "achievements",
            "achievements_for_del",
        )

    def update(self, instance, validated_data):
        achievements = validated_data.get("achievements")
        for achievement in achievements:
            if achievement['achievement_type'].get('uid'):
                achievement['achievement_type'] = achievement['achievement_type'].get('uid')
            if achievement['level'].get('uid'):
                achievement['level'] = achievement['level'].get('uid')

            models.Achievement.objects.get_or_create(
                profile=instance,
                level_id=achievement["level"],
                achievement_type_id=achievement["achievement_type"],
                content=achievement["content"],
                is_active=True,
            )

        achievements_for_del = validated_data.get("achievements_for_del")
        models.Achievement.objects.filter(pk__in=achievements_for_del).update(
            is_active=False
        )

        return instance


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = (
            "uid",
            "avatar",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        profile = request.user.profile

        image = validated_data["avatar"]
        extension = image.name.split(".")[-1]
        image_name = "{}.{}".format(str(uuid4()), extension)

        profile.avatar.save(image_name, image, save=True)
        return profile


class ModeratorChangeAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ['avatar']

    def create(self, validated_data):
        request = self.context.get('request')
        profile = request.user.profile
        if profile.role.is_mod and settings.MODERATOR_CAN_EDIT:
            applicant_profile_uid = request.data.get('profile')
            applicant_profile = models.Profile.objects.get(pk=applicant_profile_uid)
            image = validated_data["avatar"]
            extension = image.name.split(".")[-1]
            image_name = "{}.{}".format(str(uuid4()), extension)
            applicant_profile.avatar.save(image_name, image, save=True)
            return profile
        else:
            raise Exception("if moderator and can upload avatars")


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = (
            "academic_degree",
            "academic_rank",
            "work_experience_year",
            "work_experience_month",
        )


class TeacherPositionSerializer(serializers.ModelSerializer):
    position = serializers.CharField()
    cathedra = serializers.CharField()

    class Meta:
        model = models.TeacherPosition
        fields = (
            # 'teacher',
            "position",
            "cathedra",
            "is_main",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.is_main:
            data['work'] = _('Основное место работы')
        else:
            data['work'] = _('Совместительство')

        return data


class TeacherShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = (
            "uid",
            "full_name",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["name"] = "{} {}.".format(instance.last_name, instance.first_name[0])

        try:
            middle_name = instance.middle_name[0]
            data["name"] += "{}.".format(middle_name)
        except IndexError:
            pass

        return data


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Gender
        fields = "__all__"


class MaritalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MaritalStatus
        fields = "__all__"


class ProfilePhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProfilePhone
        fields = ["phone_type", "value"]


class PhoneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhoneType
        fields = "__all__"


class ControlFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.ControlForm
        fields = (
            'uid',
            'name',
            'is_exam',
            'is_course_work',
            'is_gos_exam',
            'is_diploma',
        )


class StudentDisciplineControlFormSerializer(serializers.ModelSerializer):
    """Используется для вывода Дисциплин Студентов для выбора Формы контроля"""

    discipline = serializers.CharField(read_only=True)
    status = StudentDisciplineStatusSerializer()

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            'discipline',
            'status',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['status_d'] = None

        try:
            discipline_credit = org_models.DisciplineCredit.objects.get(
                study_plan=instance.study_plan,
                cycle=instance.cycle,
                discipline=instance.discipline,
                acad_period=instance.acad_period,
                student=instance.student,
            )
            if discipline_credit.status:
                data['status_d'] = StudentDisciplineStatusSerializer(discipline_credit.status).data
        except org_models.DisciplineCredit.DoesNotExist:
            raise CustomException(detail='not_found')
        except org_models.DisciplineCredit.MultipleObjectsReturned:
            discipline_credit = org_models.DisciplineCredit.objects.filter(
                study_plan=instance.study_plan,
                cycle=instance.cycle,
                discipline=instance.discipline,
                acad_period=instance.acad_period,
                student=instance.student,
            ).first()
            if discipline_credit.status:
                data['status_d'] = StudentDisciplineStatusSerializer(discipline_credit.status).data

        if not data['status_d']:
            data['status_d'] = StudentDisciplineStatusSerializer(
                org_models.StudentDisciplineStatus.objects.get(number=1)).data
        control_form_pks = org_models.DisciplineCreditControlForm.objects.filter(
            discipline_credit=discipline_credit.uid,
        ).values('control_form')
        control_forms = org_models.ControlForm.objects.filter(pk__in=control_form_pks)
        serializer = ControlFormSerializer(control_forms,
                                           many=True)
        data['select'] = serializer.data
        chosen_control_forms = discipline_credit.chosen_control_forms.all()
        chosen_control_forms_data = ControlFormSerializer(chosen_control_forms,
                                                          many=True).data
        chosen_control_forms_list = [item['uid'] for item in chosen_control_forms_data]
        data['chosen_control_forms'] = chosen_control_forms_list
        data['listStatus'] = dict()

        statuses = org_models.StudentDisciplineStatus.objects.filter(is_active=True)
        for item in statuses:
            data['listStatus'][item.number] = item.name

        data['discipline_credit'] = discipline_credit.uid
        data['hide'] = False
        data['loader'] = False

        return data


class ChooseControlFormSerializer(serializers.ModelSerializer):
    """Выбор формы контроля"""

    class Meta:
        model = org_models.DisciplineCredit
        fields = (
            'uid',
            'chosen_control_forms',
            'status',
            # 'teacher',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        status = org_models.StudentDisciplineStatus(uid=data['status'])
        data['status'] = {'uid': status.uid, 'number': status.number, 'name': status.name}
        return data

    def update(self, instance, validated_data):
        chosen_control_forms = validated_data.get('chosen_control_forms')
        status = validated_data.get('status')
        instance.chosen_control_forms.set(chosen_control_forms)
        instance.status = status
        instance.save()
        return instance


class ProfileForAdviserSerializer(serializers.ModelSerializer):
    """Список студентов для полного списка адвайзеру"""
    status = serializers.CharField()

    class Meta:
        model = models.Profile
        fields = (
            'uid',
            'first_name',
            'last_name',
            'middle_name',
            'birth_date',
            'status',
        )


class StudentStatusListSerializer(serializers.ModelSerializer):
    """
    Список статуса студента
    """

    class Meta:
        model = models.StudentStatus
        fields = (
            'uid',
            'name',
        )


class GenderListSerializer(serializers.ModelSerializer):
    """
    Список пола пользователей
    """

    class Meta:
        model = models.Gender
        fields = (
            'uid',
            'name',
        )


class CitizenshipListSerializer(serializers.ModelSerializer):
    """
    Список национальностей полбзователей
    """

    class Meta:
        model = common_models.Citizenship
        fields = (
            'uid',
            'name',
        )


