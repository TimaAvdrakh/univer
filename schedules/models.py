from django.db import models
from common.models import BaseCatalog, BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class RoomType(BaseCatalog):
    class Meta:
        verbose_name = 'Тип помещения'
        verbose_name_plural = 'Типы помещений'


class Room(BaseCatalog):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    department = GenericForeignKey(
        'content_type',
        'object_id',
    )
    type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        verbose_name='Тип помещения',
        related_name='rooms',
    )
    capacity = models.IntegerField(
        verbose_name='Вместимость ',
    )

    def __str__(self):
        return '{} - {}'.format(self.name,
                                self.capacity)

    class Meta:
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'


class TimeWindow(BaseCatalog):
    from_time = models.TimeField(
        verbose_name='Время с',
    )
    to_time = models.TimeField(
        verbose_name='Время по',
    )

    class Meta:
        verbose_name = 'Временное окно'
        verbose_name_plural = 'Временные окна'


class GradingSystem(BaseCatalog):
    class Meta:
        verbose_name = 'Система оценивания'
        verbose_name_plural = 'Системы оценивании'


class LessonStatus(BaseCatalog):
    class Meta:
        verbose_name = 'Статус занятия'
        verbose_name_plural = 'Статусы занятий'


class Lesson(BaseModel):
    flow_uid = models.UUIDField(
        verbose_name='UID потока',
    )
    date = models.DateField(
        verbose_name='Дата занятия',
    )
    time = models.ForeignKey(
        TimeWindow,
        on_delete=models.CASCADE,
        verbose_name='Время занятия',
    )
    discipline = models.ForeignKey(
        'organizations.Discipline',
        on_delete=models.CASCADE,
        verbose_name='Дисциплина',
    )
    teacher = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Преподаватель',
    )
    language = models.ForeignKey(
        'organizations.Language',
        on_delete=models.CASCADE,
        verbose_name='Язык преподавания',
    )
    classroom = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name='Аудитория',
    )
    group = models.ForeignKey(
        'organizations.Group',
        on_delete=models.CASCADE,
        verbose_name='Группа',
    )
    load_type = models.ForeignKey(
        'organizations.LoadType2',
        on_delete=models.CASCADE,
    )
    acad_period = models.ForeignKey(
        'organizations.AcadPeriod',
        on_delete=models.CASCADE,
        verbose_name='Академический период',
    )
    study_year = models.ForeignKey(
        'organizations.StudyPeriod',
        on_delete=models.CASCADE,
        verbose_name='Учебный год',
    )
    grading_system = models.ForeignKey(
        GradingSystem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Система оценивания',
    )
    subject = models.CharField(
        max_length=500,
        default='',
        blank=True,
        verbose_name='Тема',
    )
    status = models.ForeignKey(
        LessonStatus,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Статус занятия',
    )

    def __str__(self):
        return '{}'.format(self.subject)

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
