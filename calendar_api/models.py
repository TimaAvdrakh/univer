from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage, send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Case, When, Value, Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from common.models import (
    BaseModel,
    BaseCatalog,
    Comment,
    Citizenship,
    Nationality,
    Changelog
)
from portal_users.models import (
    Profile,
    Gender,
    Role
)
from schedules.models import (
    Room
)


class RepetitionTypes(BaseCatalog):
    class Meta:
        verbose_name = 'Тип повторения события',

    def __str__(self):
        return f'{self.name}'


class Events(BaseCatalog):
    event_start = models.DateTimeField(
        default=False,
        verbose_name='Дата и время начала события',
    )
    event_end = models.DateTimeField(
        default=False,
        verbose_name='Дата и время конец события',
    )
    event_place = models.TextField(
        default=False,
        blank=True,
        null=True,
        verbose_name='Место проведения'
    )
    creator = models.ForeignKey(
        Profile,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Автор события',
        related_name='events_creator'
    )
    participants = models.ManyToManyField(
        Profile,
        verbose_name='Участники события',
        related_name='events_participants',

    )
    notification = models.BooleanField(
        default=False,
        verbose_name='Уведомления участникам',
    )
    event_description = models.TextField(
        default=False,
        blank=True,
        null=True,
        verbose_name='Описание события',
    )
    reserve_auditory = models.ForeignKey(
        Room,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Забранированная аудитория'
    )
    repetition_type = models.ForeignKey(
        RepetitionTypes,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Тип повторения события',
    )

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return f'{self.name} созданно {self.creator.name}'
