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
from organizations.models import (
    Group,
    Faculty,
    Cathedra,
    EducationProgram,
    EducationProgramGroup,
)


class RepetitionTypes(BaseCatalog):
    class Meta:
        verbose_name = 'Тип повторения события',
        verbose_name_plural = 'Тип повторения событий',

    def __str__(self):
        return self.name


class Participants(BaseModel):
    """
    Данная модель отвечает за включение пользователей в список участников мироприятия.
    В данной модели поля привязаны к users.Profile, organizations.Group,
    organizations.Faculty, organizations.Cathedra, organizations.EducationProgramGroup,
    organizations.EducationGroup
    """

    participant_profiles = models.ManyToManyField(
        Profile,
        blank=True,
        verbose_name="Профили участников события",
        related_name="event_participant_profiles",
    )

    group = models.ManyToManyField(
        Group,
        blank=True,
        verbose_name="Учебная группа",
        related_name="event_groups",
    )

    faculty = models.ManyToManyField(
        Faculty,
        blank=True,
        verbose_name="Факультет",
        related_name="events_faculty",
    )

    cathedra = models.ManyToManyField(
        Cathedra,
        blank=True,
        verbose_name="Кафедра",
        related_name="events_cathedra",
    )

    education_programs = models.ManyToManyField(
        EducationProgram,
        blank=True,
        verbose_name="Образовательная программа",
        related_name="events_education_program",
    )

    education_program_groups = models.ManyToManyField(
        EducationProgramGroup,
        blank=True,
        verbose_name="Группа образовательных программ",
        related_name="events_education_program_groups",
    )

    class Meta:
        verbose_name = "Участник события"
        verbose_name_plural = "Участники события"


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
    participants = models.ForeignKey(
        Participants,
        on_delete=models.CASCADE,
        verbose_name='Участники события',
        blank=True,
        null=True,
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
        return f'{self.name} созданно {self.creator.full_name}'
