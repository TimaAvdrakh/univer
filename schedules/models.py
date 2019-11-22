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
    object_id = models.UUIDField(null=True)
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
        return '{} ({})'.format(self.name,
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

    def __str__(self):
        return '{} {} - {}'.format(self.name,
                                   self.from_time,
                                   self.to_time)

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
    teachers = models.ManyToManyField(
        'portal_users.Profile',
        verbose_name='Преподаватели',
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
    groups = models.ManyToManyField(
        'organizations.Group',
        verbose_name='Группы',
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
    intermediate_control = models.BooleanField(
        default=False,
        verbose_name='Промежуточный контроль',
    )

    def __str__(self):
        return '{} {}'.format(self.discipline.name,
                              self.subject)

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'


class Mark(BaseCatalog):
    weight = models.FloatField(
        verbose_name='Вес оценки',
    )
    grading_system = models.ForeignKey(
        GradingSystem,
        on_delete=models.CASCADE,
        verbose_name='Система оценивания',
    )
    value_letter = models.CharField(
        max_length=200,
        verbose_name='Оценка по буквенной системе',
    )
    value_number = models.FloatField(
        verbose_name='Цифровой эквивалент',
    )
    value_traditional = models.CharField(
        max_length=200,
        verbose_name='Оценка по традиционной системе',
    )

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'


class StudentPerformance(BaseModel):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name='Занятие',
    )
    student = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Студент',
    )
    mark = models.ForeignKey(
        Mark,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Оценка',
    )
    missed = models.BooleanField(
        default=False,
        verbose_name='Отсутствовал',
    )
    reason = models.CharField(
        max_length=500,
        default='',
        blank=True,
        verbose_name='Причина отсутствия',
    )

    def __str__(self):
        return '{} {}'.format(self.student.first_name,
                              self.lesson.discipline.name)

    class Meta:
        verbose_name = 'Успеваемость студента'
        verbose_name_plural = 'Успеваемости студентов'
