from django.db import models
from django.contrib.auth.models import User
from .utils import get_sentinel_user
from django.contrib.postgres.fields import JSONField
from uuid import uuid4


class BaseModel(models.Model):
    class Meta:
        abstract = True

    uid = models.UUIDField(
        verbose_name='Уникальный идентификатор',
        primary_key=True,
        editable=False,
        default=uuid4,
        unique=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    deleted = models.DateTimeField(
        null=True,
        blank=True,
    )


class BaseCatalog(BaseModel):
    # univer = models.ForeignKey(
    #     'organizations.Organization',
    #     on_delete=models.CASCADE,
    #     default=''
    # )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Nationality(BaseCatalog):
    class Meta:
        verbose_name = 'Национальность'
        verbose_name_plural = 'Национальности'


class Citizenship(BaseCatalog):
    class Meta:
        verbose_name = 'Гражданство'
        verbose_name_plural = 'Гражданство'


class DocumentType(BaseCatalog):
    class Meta:
        verbose_name = 'Тип документа'
        verbose_name_plural = 'Типы документа'


class GovernmentAgency(BaseCatalog):
    class Meta:
        verbose_name = 'Государственная организация'
        verbose_name_plural = 'Государственные организации'


class IdentityDocument(BaseModel):
    profile = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        on_delete=models.CASCADE,
        related_name='identity_documents',
        verbose_name='Пользователь',
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.CASCADE,
        verbose_name='Тип документа',
    )
    serial_number = models.CharField(
        max_length=100,
        verbose_name='Серия',
    )
    number = models.CharField(
        max_length=100,
        verbose_name='Номер',
    )
    given_date = models.DateField(
        null=True,
        verbose_name='Дата выдачи',
    )
    validity_date = models.DateField(
        verbose_name='Срок действия',
    )
    issued_by = models.ForeignKey(
        GovernmentAgency,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Кем выдан',
    )

    def __str__(self):
        return '{}'.format(self.profile.full_name,
                           self.document_type)

    class Meta:
        verbose_name = 'Документ удостоверяющий личность'
        verbose_name_plural = 'Документы удостоверяющий личность'


class RegistrationPeriod(BaseCatalog):
    start_date = models.DateField(
        verbose_name='Дата начала',
    )
    end_date = models.DateField(
        verbose_name='Дата завершения',
    )

    def __str__(self):
        return '{}:{}-{}'.format(self.name,
                                 self.start_date,
                                 self.end_date)

    def save(self, *args, **kwargs):
        if self.start_date >= self.end_date:
            """Предупреждение выдавать"""
            pass
        else:
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Период регистрации'
        verbose_name_plural = 'Периоды регистрации'


class CourseAcadPeriodPermission(BaseModel):
    registration_period = models.ForeignKey(
        RegistrationPeriod,
        on_delete=models.CASCADE,
        related_name='course_acad_periods',
        verbose_name='Период регистрации',
    )
    course = models.PositiveSmallIntegerField(
        verbose_name='Курс',
    )
    acad_period = models.ForeignKey(
        'organizations.AcadPeriod',
        on_delete=models.CASCADE,
        verbose_name='Академический период',
    )

    def __str__(self):
        return '{}: {}-{}'.format(self.registration_period,
                                  self.course,
                                  self.acad_period)

    class Meta:
        verbose_name = 'Правила выбора Курс-Акад.период'
        verbose_name_plural = 'Правила выбора Курс-Акад.период'
        unique_together = (
            'course',
            'acad_period',
        )


# class Log(BaseModel):
#     obj_uid = models.CharField()
#     model_name = models.CharField()
#     author = models.ForeignKey(
#         User,
#         on_delete=models.SET(get_sentinel_user),
#         verbose_name='Автор',
#         related_name='my_actions',
#     )
#     date = models.DateTimeField(
#         auto_now_add=True,
#     )
#     content = JSONField(
#         verbose_name='Контент',
#     )
#
#     def __str__(self):
#         return '{} - {}'.format(self.obj_uid, self.author.username)
#
#     class Meta:
#         verbose_name = 'Лог'
#         verbose_name_plural = 'Логи'
