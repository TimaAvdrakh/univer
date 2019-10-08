from django.db import models
from common.models import BaseModel, BaseCatalog
from django.contrib.auth.models import User
from uuid import uuid4
from organizations import models as org_models
from common.utils import get_sentinel_user


class Gender(BaseCatalog):
    class Meta:
        verbose_name = 'Пол'
        verbose_name_plural = 'Полы'


class MaritalStatus(BaseCatalog):
    class Meta:
        verbose_name = 'Семейное положение'
        verbose_name_plural = 'Семейное положение'


class Profile(BaseModel):
    user = models.OneToOneField(
        User,
        related_name='profile',
        on_delete=models.CASCADE,
    )
    student_id = models.IntegerField(
        null=True,
        verbose_name='ID студента',
        help_text='Из 1С',
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
    )
    middle_name = models.CharField(
        max_length=100,
        verbose_name='Отчество',
        default='',
        blank=True,
    )
    first_name_en = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name='Имя на английском',
    )
    last_name_en = models.CharField(
        max_length=100,
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
        max_length=200,
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
        max_length=50,
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
        max_length=20,
        default='',
        blank=True,
        verbose_name='Телефон',
    )
    email = models.EmailField(
        verbose_name='Email',
        default='',
        blank=True,
    )
    skype = models.CharField(
        max_length=100,
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
        max_length=100,
        default='',
        blank=True,
        verbose_name='Ученая степень',
    )
    academic_rank = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name='Ученое звание',
    )
    work_experience_year = models.CharField(
        default='',
        blank=True,
        max_length=100,
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
    teacher = models.ForeignKey(
        Teacher,
        models.CASCADE,
        verbose_name='Сотрудник',
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

    def __str__(self):
        return '{} {}'.format(self.teacher.profile.full_name,
                              self.position)

    class Meta:
        verbose_name = 'Должность сотрудника'
        verbose_name_plural = 'Должности сотрудников'


class Interest(BaseCatalog):
    profile = models.ForeignKey(
        Profile,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Профиль',
        related_name='interests',
    )

    class Meta:
        verbose_name = 'Увлечение'
        verbose_name_plural = 'Увлечения'


class Role(BaseModel):
    organization = models.ForeignKey(
        org_models.Organization,
        on_delete=models.CASCADE,
        verbose_name='Организация',
        related_name='roles',
    )
    profile = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        on_delete=models.CASCADE,
        related_name='roles',
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
        verbose_name='Супервизор',
    )

    def __str__(self):
        return '{} {}'.format(self.organization.name,
                              self.profile.user.username)

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class ResetPassword(BaseModel):
    email = models.EmailField(
        verbose_name='Email',
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
