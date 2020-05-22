from django.db import models
from common.models import BaseModel, BaseCatalog
from django.contrib.auth.models import User
from uuid import uuid4
from organizations import models as org_models
from common.utils import get_sentinel_user
from common.utils import password_generator
from cron_app.models import CredentialsEmailTask
from django.db.models import Max
from validate_email import validate_email
from portal.curr_settings import INACTIVE_STUDENT_STATUSES
from schedules.models import LessonStudent


class Gender(BaseCatalog):
    class Meta:
        verbose_name = 'Пол'
        verbose_name_plural = 'Полы'


class MaritalStatus(BaseCatalog):
    class Meta:
        verbose_name = 'Семейное положение'
        verbose_name_plural = 'Семейное положение'


class StudentStatus(BaseCatalog):
    class Meta:
        verbose_name = 'Статус студента'
        verbose_name_plural = 'Статусы студентов'


class UsernameRule(BaseModel):
    raw_username = models.CharField(
        max_length=500,
        verbose_name='Логин',
    )
    order = models.IntegerField(
        verbose_name='Порядок',
    )

    def __str__(self):
        return '{}_{}'.format(self.raw_username,
                              self.order)

    class Meta:
        verbose_name = 'Правило создания логина'
        verbose_name_plural = 'Правила создания логина'


class UserCredential(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    password = models.CharField(
        max_length=50,
        verbose_name='Пароль',
    )

    class Meta:
        verbose_name = 'Пароль пользователя'
        verbose_name_plural = 'Пароли пользователей'


class Profile(BaseModel):
    user = models.OneToOneField(
        User,
        null=True,
        related_name='profile',
        on_delete=models.CASCADE,
    )
    student_id = models.IntegerField(
        null=True,
        verbose_name='ID студента',
        help_text='Из 1С',
    )
    first_name = models.CharField(
        max_length=200,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=200,
        verbose_name='Фамилия',
    )
    middle_name = models.CharField(
        max_length=200,
        verbose_name='Отчество',
        null=True,
        blank=True,
    )
    first_name_en = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='Имя на английском',
    )
    last_name_en = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='Фамилия на английском',
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения',
    )
    birth_place = models.CharField(
        max_length=500,
        default='',
        blank=True,
        verbose_name='Место рождения',
    )
    nationality = models.ForeignKey(
        'common.Nationality',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Национальность',
    )
    citizenship = models.ForeignKey(
        'common.Citizenship',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Гражданство',
    )
    gender = models.ForeignKey(
        Gender,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Пол',
        related_name='profiles',
    )
    marital_status = models.ForeignKey(
        MaritalStatus,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='profiles',
        verbose_name='Семейное положение',
    )
    iin = models.CharField(
        max_length=100,
        verbose_name='ИИН',
        null=True,
        blank=True,
    )
    course = models.PositiveSmallIntegerField(
        verbose_name='Курс',
        default=1,
    )
    address = models.CharField(
        max_length=500,
        default='',
        blank=True,
        verbose_name='Адрес',
    )
    phone = models.CharField(
        max_length=50,
        default='',
        blank=True,
        verbose_name='Телефон',
    )
    email = models.EmailField(
        verbose_name='Email',
        default='',
        blank=True,
        # unique=True,
    )
    skype = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='Skype',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name='Аватар',
        blank=True,
        null=True,
    )
    extra_data = models.CharField(
        max_length=1000,
        default='',
        blank=True,
        verbose_name='Дополнительная информация',
    )
    status = models.ForeignKey(
        StudentStatus,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Статус студента',
    )
    login_sent = models.BooleanField(
        default=False,
        verbose_name='Логин отправлен',
    )
    password_changed = models.NullBooleanField(
        default=False,
        verbose_name='Сменил пароль',
    )
    notify_me_from_email = models.NullBooleanField(
        default=True,
        verbose_name='Оповещать по почте',
    )

    def save(self, *args, **kwargs):
        if self.exchange:
            if self.user is None:
                password = password_generator(size=8)
                raw_username = '{}{}'.format(self.last_name,
                                             self.first_name[0])
                if len(self.middle_name) > 0:
                    raw_username += self.middle_name[0]

                if not UsernameRule.objects.filter(raw_username=raw_username).exists():
                    UsernameRule.objects.create(
                        raw_username=raw_username,
                        order=0,
                    )
                    username = raw_username
                else:
                    max_order = UsernameRule.objects.filter(raw_username=raw_username).aggregate(max_order=Max('order'))[
                        'max_order']
                    new_max = max_order + 1
                    UsernameRule.objects.create(
                        raw_username=raw_username,
                        order=new_max,
                    )

                    username = '{}_{}'.format(raw_username,
                                              new_max)

                user = User.objects.create(
                    username=username,
                    email=self.email,
                    # first_name=self.first_name,
                    # last_name=self.last_name,
                )
                user.set_password(password)
                user.save()
                self.user = user

                UserCredential.objects.create(
                    user=self.user,
                    password=password,
                )

                if len(self.email) > 0 and validate_email(self.email):
                    CredentialsEmailTask.objects.create(
                        to=self.email,
                        username=user.username,
                        password=password,
                    )
                    self.login_sent = True

            else:
                if not self.login_sent:
                    if len(self.email) > 0 and validate_email(self.email):
                        user_credential = UserCredential.objects.get(user=self.user)

                        CredentialsEmailTask.objects.create(
                            to=self.email,
                            username=self.user.username,
                            password=user_credential.password,
                        )
                        self.login_sent = True

            if self.status_id in INACTIVE_STUDENT_STATUSES:
                """Если статус профиля в списке неактивных студентов,
                то записи LessonStudent с участием данного студента декативируются"""
                LessonStudent.objects.filter(is_active=True,
                                             student=self).update(is_active=False)

        if self.user:
            self.user.email = self.email
            self.user.save()

        super(Profile, self).save()

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """ФИО"""
        return '{} {} {}'.format(
            self.last_name,
            self.first_name,
            self.middle_name
        )


    @property
    def name_initial(self):
        """Фамилия инициалы"""
        name = '{} {}.'.format(self.last_name,
                               self.first_name[0])
        if len(self.middle_name) > 0:
            name += '{}.'.format(self.middle_name[0])
        return name

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Teacher(BaseModel):
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        verbose_name='Профиль',
    )
    academic_degree = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='Ученая степень',
    )
    academic_rank = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='Ученое звание',
    )
    work_experience_year = models.CharField(
        default='',
        blank=True,
        max_length=200,
        verbose_name='Стаж работы в ВУЗ (Год)',
    )
    work_experience_month = models.CharField(
        default='',
        blank=True,
        max_length=100,
        verbose_name='Стаж работы в ВУЗ (Месяц)',
    )

    def __str__(self):
        return '{} {}'.format(self.profile.full_name,
                              self.academic_degree)

    class Meta:
        verbose_name = 'Cотрудник'
        verbose_name_plural = 'Cотрудники'


class Position(BaseCatalog):
    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class TeacherPosition(BaseModel):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Профиль'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        verbose_name='Должность',
    )
    cathedra = models.ForeignKey(
        'organizations.Cathedra',
        on_delete=models.CASCADE,
        verbose_name='Подразделение',
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='Основная должность',
    )
    study_year = models.ForeignKey(
        'organizations.StudyPeriod',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Учебный год',
    )

    # def save(self, *args, **kwargs):
    #     if self.exchange:
    #         self.uid = uuid4()
    #
    #     super(TeacherPosition, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {}'.format(self.profile.full_name,
                              self.position)

    class Meta:
        verbose_name = 'Должность сотрудника'
        verbose_name_plural = 'Должности сотрудников'
        unique_together = (
            'profile',
            'position',
            'cathedra',
            'study_year',
            # 'is_main',
        )


class Interest(BaseCatalog):
    profile = models.ForeignKey(
        Profile,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Профиль',
        related_name='interests'
    )

    class Meta:
        unique_together = [['profile', 'name']]
        indexes = [
            models.Index(fields=['profile']),
        ]
        verbose_name = 'Увлечение'
        verbose_name_plural = 'Увлечения'


class Role(BaseModel):
    organization = models.ForeignKey(
        org_models.Organization,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Организация',
        related_name='roles',
    )
    profile = models.OneToOneField(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        null=True,
        related_name='role',
        verbose_name='Пользователь',
    )
    is_student = models.BooleanField(
        default=False,
        verbose_name='Студент',
    )
    is_teacher = models.BooleanField(
        default=False,
        verbose_name='Преподаватель',
    )
    is_org_admin = models.BooleanField(
        default=False,
        verbose_name='Администратор организации',
    )
    is_supervisor = models.BooleanField(
        default=False,
        verbose_name='Эдвайзор',
    )
    is_applicant = models.BooleanField(
        default=False,
        verbose_name='Абитуриент'
    )
    is_mod = models.BooleanField(
        default=False,
        verbose_name='Модератор'
    )

    def __str__(self):
        return '{}'.format(self.profile.user.username)

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class ResetPassword(BaseModel):
    email = models.EmailField(
        default='',
        blank=True,
        verbose_name='Email',
    )
    username = models.CharField(
        max_length=150,
        default='',
        verbose_name='Логин',
    )
    uuid = models.UUIDField(
        default=uuid4,
        verbose_name='UUID',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    changed = models.BooleanField(
        default=False,
        verbose_name='Изменен',
    )

    class Meta:
        verbose_name = 'Восстановление пароля'
        verbose_name_plural = 'Восстановление пароля'


class OrganizationToken(BaseModel):
    organization = models.ForeignKey(
        org_models.Organization,
        on_delete=models.CASCADE,
        verbose_name='Организация',
        related_name='tokens',
    )
    token = models.CharField(
        max_length=40,
        default=uuid4,
        verbose_name='Токен',
    )

    def __str__(self):
        return 'Token для {}'.format(self.organization.name)

    class Meta:
        verbose_name = 'Токен для Организации'
        verbose_name_plural = 'Токены для Организации'


class Level(BaseCatalog):
    class Meta:
        verbose_name = 'Уровень'
        verbose_name_plural = 'Уровень'


class AchievementType(BaseCatalog):
    class Meta:
        verbose_name = 'Тип достижения'
        verbose_name_plural = 'Типы достижения'


class Achievement(BaseModel):
    profile = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Пользователь',
    )
    achievement_type = models.ForeignKey(
        AchievementType,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Тип достижения',
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Уровень',
    )
    content = models.CharField(
        max_length=1000,
        verbose_name='Тело',
    )

    def __str__(self):
        return '{} {}'.format(self.profile.user.get_full_name(),
                              self.achievement_type)

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'


class PhoneType(BaseCatalog):
    class Meta:
        verbose_name = 'Тип телефона'
        verbose_name_plural = 'Типы телефона'


class ProfilePhone(BaseModel):
    profile = models.ForeignKey(
        Profile,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Профиль',
        related_name='phones',
    )
    phone_type = models.ForeignKey(
        PhoneType,
        on_delete=models.CASCADE,
        verbose_name='Тип телефона',
        related_name='phones',
    )
    value = models.CharField(
        max_length=50,
        verbose_name='Номер телефона',
    )

    # def save(self, *args, **kwargs):
    #     if self.exchange and self._state.adding:
    #         self.uid = uuid4()
    #
    #     super(ProfilePhone, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {}'.format(self.profile.first_name,
                              self.value)

    class Meta:
        verbose_name = 'Телефон Пользователя'
        verbose_name_plural = 'Телефоны Пользователей'
        unique_together = (
            'profile',
            'phone_type',
            'value',
        )


class InfoShowPermission(BaseModel):
    profile = models.ForeignKey(
        Profile,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Профиль',
        related_name='info_show_permission',
    )
    first_name_en = models.BooleanField(
        default=True,
        verbose_name='Имя',
    )
    last_name_en = models.BooleanField(
        default=True,
        verbose_name='Фамилия',
    )
    birth_date = models.BooleanField(
        default=True,
        verbose_name='Дата рождения',
    )
    birth_place = models.BooleanField(
        default=True,
        verbose_name='Место рождения',
    )
    nationality = models.BooleanField(
        default=True,
        verbose_name='Национальность',
    )
    citizenship = models.BooleanField(
        default=True,
        verbose_name='Гражданство',
    )
    gender = models.BooleanField(
        default=True,
        verbose_name='Пол',
    )
    marital_status = models.BooleanField(
        default=True,
        verbose_name='Семейное положение',
    )
    address = models.BooleanField(
        default=True,
        verbose_name='Адрес',
    )
    phone = models.BooleanField(
        default=True,
        verbose_name='Телефон',
    )
    email = models.BooleanField(
        default=True,
        verbose_name='Email',
    )
    skype = models.BooleanField(
        default=True,
        verbose_name='Skype',
    )
    interests = models.BooleanField(
        default=True,
        verbose_name='Интересы'
    )
    extra_data = models.BooleanField(
        default=True,
        verbose_name='Дополнительная информация',
    )
    iin = models.BooleanField(
        default=False,
        verbose_name='ИИН',
    )
    identity_documents = models.BooleanField(
        default=False,
        verbose_name='Документ',
    )
    educations = models.BooleanField(
        default=True,
        verbose_name='Информация об образовании',
    )

    def __str__(self):
        return "{} {} {}".format(
            self.profile.first_name,
            self.profile.last_name,
            self.profile.middle_name,
        )

    class Meta:
        verbose_name = 'Разрешение для отображения инфо пользователя'
        verbose_name_plural = 'Разрешения для отображения инфо пользователя'
