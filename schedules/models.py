from django.db import models
from common.models import BaseCatalog, BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from organizations.models import Group, LoadType2
from portal.curr_settings import lesson_statuses, INACTIVE_STUDENT_STATUSES


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


class ElectronicJournal(BaseModel):
    flow_uid = models.UUIDField(
        null=True,
        verbose_name='UID потока',
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
    study_year = models.ForeignKey(
        'organizations.StudyPeriod',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Учебный год',
    )
    plan_block_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата запланированной блокировки',
    )
    block_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата блокировки',
    )

    # stud_disciplines = models.ManyToManyField(
    #     'organizations.StudentDiscipline',
    #     verbose_name='Дисциплины студентов',
    # )

    def __str__(self):
        return '{} {}'.format(self.discipline,
                              self.load_type)

    def close_lessons(self):
        """Закрываем всех занятии ЭЖ"""
        self.lessons.filter(is_active=True).update(closed=True,
                                                   admin_allow=False)

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
    closed = models.BooleanField(
        default=False,
        verbose_name='Закрыт',
    )
    admin_allow = models.BooleanField(
        default=False,
        verbose_name='Разрешение админа',
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

        super(Lesson, self).save(*args, **kwargs)

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
        default='',
        blank=True,
        verbose_name='Оценка по буквенной системе',
    )
    value_number = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Цифровой эквивалент',
    )
    value_traditional = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='Оценка по традиционной системе',
    )

    def __str__(self):
        return '{}'.format(self.weight)

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
        default=True,
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
    flow_uid = models.UUIDField(
        verbose_name='UID потока',
        null=True,
    )
    teacher = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Преподаватель',
    )

    def save(self, *args, **kwargs):
        if self.exchange:
            if self.is_active:
                lessons = Lesson.objects.filter(is_active=True,
                                                flow_uid=self.flow_uid)
                for lesson in lessons:
                    lesson.teachers.add(self.teacher)
            else:
                lessons = Lesson.objects.filter(is_active=True,
                                                flow_uid=self.flow_uid)
                for lesson in lessons:
                    try:
                        lesson.teachers.remove(self.teacher)
                    except:
                        pass
        super(LessonTeacher, self).save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.flow_uid,
                                self.teacher.first_name)

    class Meta:
        verbose_name = 'Препод-Занятие'
        verbose_name_plural = 'Препод-Занятие'
        unique_together = (
            'flow_uid',
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
            if self.student.status_id in INACTIVE_STUDENT_STATUSES:
                """Если статус студента в списке неактивных студентов, запись не создается"""
                return

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
