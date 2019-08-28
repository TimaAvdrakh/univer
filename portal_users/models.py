from django.db import models
from common.models import BaseModel
from django.contrib.auth.models import User
from uuid import uuid4
from organizations.models import Organization, StudyForm
from common.utils import get_sentinel_user


class Gender(BaseModel):
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пол'
        verbose_name_plural = 'Полы'


class MaritalStatus(BaseModel):
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Семейное положение'
        verbose_name_plural = 'Семейное положение'


class Profile(BaseModel):
    user = models.OneToOneField(
        User,
        related_name='profile',
        on_delete=models.CASCADE,
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
    nationality = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name='Национальность',
    )
    citizenship = models.CharField(
        max_length=100,
        default='',
        blank=True,
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
    iin = models.IntegerField(
        verbose_name='ИИН',
        null=True,
        blank=True,
    )
    document = models.CharField(
        max_length=500,
        default='',
        blank=True,
        verbose_name='Документ, удостоверяющий личность'
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
    interest = models.CharField(
        max_length=1000,
        default='',
        blank=True,
        verbose_name='Увлечения',
    )

    # Обучение
    entry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата поступления в ВУЗ',
    )
    study_form = models.ForeignKey(
        StudyForm,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Форма обучения',
        related_name='profiles',
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Role(BaseModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name='Организация',
        related_name='roles',
    )
    user = models.ForeignKey(
        User,
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
                              self.user.username)

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
