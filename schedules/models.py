from django.db import models
from common.models import BaseCatalog, BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from organizations.models import Group, LoadType2
from portal.curr_settings import lesson_statuses


class RoomType(BaseCatalog):
    class Meta:
        verbose_name = 'Тип помещения'
        verbose_name_plural = 'Типы помещений'


class Room(BaseCatalog):  # TODO FOR 1C
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
    number = models.SmallIntegerField(
        default=0,
        verbose_name='Номер',
    )

    class Meta:
        verbose_name = 'Система оценивания'
        verbose_name_plural = 'Системы оценивании'


class LessonStatus(BaseCatalog):
    class Meta:
        verbose_name = 'Статус занятия'
        verbose_name_plural = 'Статусы занятий'


# class JournalStatus(BaseCatalog):
#     class Meta:
#         verbose_name = 'Статус журнала'
#         verbose_name_plural = 'Статусы журналов'


class ElectronicJournal(BaseModel):
    flow_uid = models.UUIDField(
        null=True,
        verbose_name='UID потока',
    )
    teachers = models.ManyToManyField(
        'portal_users.Profile',
        verbose_name='Преподаватели',
    )
    discipline = models.ForeignKey(
        'organizations.Discipline',
        on_delete=models.CASCADE,
        verbose_name='Дисциплина',
    )
    load_type = models.ForeignKey(
        'organizations.LoadType2',
        on_delete=models.CASCADE,
        verbose_name='Тип нагрузки',
    )
    closed = models.BooleanField(
        default=False,
        verbose_name='Закрыт',
    )
    # stud_disciplines = models.ManyToManyField(
    #     'organizations.StudentDiscipline',
    #     verbose_name='Дисциплины студентов',
    # )

    def __str__(self):
        return '{} {}'.format(self.discipline,
                              self.load_type)

    class Meta:
        verbose_name = 'Электронный журнал'
        verbose_name_plural = 'Электронные журналы'


class Lesson(BaseModel):
    el_journal = models.ForeignKey(
        ElectronicJournal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name='Электронный журнал',
    )
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
    load_type = models.ForeignKey(
        'organizations.LoadType2',
        on_delete=models.CASCADE,
        verbose_name='Тип нагрузки',
    )
    load_type2_uid_1c = models.CharField(
        max_length=200,
        default='',
        verbose_name='УИД 1С Типа нагрузки',
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
    groups = models.ManyToManyField(  # TODO убрать
        'organizations.Group',
        verbose_name='Группы',
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
    classroom = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name='Аудитория',
    )

    def save(self, *args, **kwargs):
        if self.exchange:
            if self._state.adding:
                self.status_id = lesson_statuses['planned']

            if self.load_type2_uid_1c:
                try:
                    load_type2 = LoadType2.objects.get(uid_1c=self.load_type2_uid_1c)
                    self.load_type = load_type2
                except LoadType2.DoesNotExist:
                    print('LoadType2 not found')

    def __str__(self):
        return '{} {}'.format(self.discipline.name,
                              self.subject)

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
        unique_together = (
            'flow_uid',
            'date',
            'time',
        )


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
        unique_together = (
            'lesson',
            'student',
        )


class StudentPerformanceLog(BaseModel):
    author = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    stud_perf = models.ForeignKey(
        StudentPerformance,
        on_delete=models.CASCADE,
        verbose_name='Успеваемость студента',
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
        return '{} {}'.format(self.author.first_name,
                              self.stud_perf)

    class Meta:
        verbose_name = 'Лог успеваемости студента'
        verbose_name_plural = 'Логи успеваемости студентов'


class LessonTeacher(BaseModel):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name='Занятие',
    )
    teacher = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Преподаватель',
    )

    def save(self, *args, **kwargs):
        if self.exchange:
            if self.is_active:
                if self.teacher not in self.lesson.teachers.filter(is_active=True):
                    self.lesson.teachers.add(self.teacher)
            else:
                try:
                    self.lesson.teachers.remove(self.teacher)
                except:
                    pass

    def __str__(self):
        return '{} - {}'.format(self.lesson.subject,
                                self.teacher.first_name)

    class Meta:
        verbose_name = 'Препод-Занятие'
        verbose_name_plural = 'Препод-Занятие'
        unique_together = (
            'lesson',
            'teacher',
        )


class LessonStudent(BaseModel):
    flow_uid = models.UUIDField(
        verbose_name='UID потока',
    )
    group_identificator = models.CharField(
        max_length=200,
        verbose_name='Идентификатор гр/подгр',
        help_text='УИД группы или название подгруппы',
    )
    group = models.ForeignKey(
        'organizations.Group',
        on_delete=models.CASCADE,
        related_name='lesson_students',
        verbose_name='Группа/Подгруппа',
    )
    parent_group = models.ForeignKey(
        'organizations.Group',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Родитель подгруппы',
    )
    is_subgroup = models.BooleanField(
        default=False,
        verbose_name='Подгруппа',
    )
    student = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Студент',
    )

    def save(self, *args, **kwargs):
        if self.exchange:
            if self.is_subgroup:  # Если пришла подгруппа, создаю подгруппу
                try:
                    group = Group.objects.get(
                        name_ru=self.group_identificator,
                        is_subgroup=True,
                        parent=self.parent_group,
                        is_active=True,
                    )
                except Group.DoesNotExist:
                    group = Group.objects.create(
                        name_ru=self.group_identificator,
                        is_subgroup=True,
                        parent=self.parent_group,
                    )

            else:  # Если пришла группа, найду группу по uid и привяжу
                group = Group.objects.get(pk=self.group_identificator)

            self.group = group

            # lessons = Lesson.objects.filter(flow_uid=self.flow_uid,
            #                                 is_active=True)
            # for lesson in lessons:
            #     if group not in lesson.groups.filter(is_active=True):
            #         lesson.groups.add(group)

        super(LessonStudent, self).save(*args, **kwargs)

    def __str__(self):
        return '{}-{}'.format(self.flow_uid,
                              self.student.first_name)

    class Meta:
        verbose_name = 'Студент Занятия'
        verbose_name_plural = 'Студенты Занятии'
        unique_together = (
            'flow_uid',
            'group_identificator',
            'student',
        )

