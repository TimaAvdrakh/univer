from django.db import models
from common.models import BaseModel, BaseCatalog, DocumentType
from django.contrib.auth.models import User
from common.utils import get_sentinel_user
from portal import curr_settings
from datetime import date
from portal_users.utils import get_current_study_year, get_current_course, get_course, divide_to_study_years
from .utils import calculate_credit
from uuid import uuid4


class Language(BaseCatalog):
    class Meta:
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'


class Organization(BaseCatalog):
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'


class DisciplineCycle(BaseCatalog):
    short_name = models.CharField(
        max_length=10,
        default='',
        verbose_name='Краткое название',
    )

    class Meta:
        verbose_name = 'Цикл дисциплины'
        verbose_name_plural = 'Циклы дисциплин'


class DisciplineComponent(BaseCatalog):
    short_name = models.CharField(
        max_length=10,
        verbose_name='Краткое название',
        default='',
    )

    class Meta:
        verbose_name = 'Компонент дисциплины'
        verbose_name_plural = 'Компоненты дисциплин'


class StudyForm(BaseCatalog):
    class Meta:
        verbose_name = 'Форма обучения'
        verbose_name_plural = 'Формы обучения'


class Faculty(BaseCatalog):
    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'


class Cathedra(BaseCatalog):
    faculty = models.ForeignKey(
        Faculty,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Факультет',
    )

    class Meta:
        verbose_name = 'Кафедра'
        verbose_name_plural = 'Кафедры'


class Group(BaseCatalog):
    headman = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='my_groups',
        verbose_name='Староста',
    )
    kurator = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Куратор',
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Язык обучения',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Родитель',
        related_name='children',
    )
    is_subgroup = models.BooleanField(
        default=False,
        verbose_name='Подгруппа',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


# class Student(BaseModel):
#     profile = models.ForeignKey(
#         'portal_users.Profile',
#         on_delete=models.CASCADE,
#         verbose_name='Профиль',
#         related_name='students',
#     )
#     group = models.ForeignKey(
#         Group,
#         on_delete=models.CASCADE,
#         verbose_name='Группа',
#         related_name='students',
#     )
#
#     def __str__(self):
#         return '{}'.format(self.profile,
#                            self.group)
#
#     class Meta:
#         verbose_name = 'Студент'
#         verbose_name_plural = 'Студенты'


class EducationBase(BaseCatalog):
    class Meta:
        verbose_name = 'Основа обучения'
        verbose_name_plural = 'Основы обучения'


class Speciality(BaseCatalog):
    code = models.CharField(
        max_length=100,
        verbose_name='Код',
    )

    class Meta:
        verbose_name = 'Направление подготовки'
        verbose_name_plural = 'Направления подготовки'


class PreparationLevel(BaseCatalog):
    class Meta:
        verbose_name = 'Уровень подготовки'
        verbose_name_plural = 'Уровни подготовок'


class EducationProgramGroup(BaseCatalog):
    code = models.CharField(
        default='',
        max_length=100,
        verbose_name='Код',
    )

    class Meta:
        verbose_name = 'Группа образовательных программ'
        verbose_name_plural = 'Группы образовательных программ'


class EducationProgram(BaseCatalog):
    code = models.CharField(
        default='',
        max_length=100,
        verbose_name='Код',
    )
    group = models.ForeignKey(
        EducationProgramGroup,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Группа ОП',
    )

    class Meta:
        verbose_name = 'Образовательная программа'
        verbose_name_plural = 'Образовательные программы'


class EducationType(BaseCatalog):
    class Meta:
        verbose_name = 'Вид образования'
        verbose_name_plural = 'Виды образования'


class Education(BaseModel):
    profile = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        on_delete=models.SET_NULL,
        related_name='educations',
        verbose_name='Пользователь',
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.CASCADE,
        verbose_name='Тип документа',
    )
    edu_type = models.ForeignKey(
        EducationType,
        on_delete=models.CASCADE,
        verbose_name='Вид образования',
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
        verbose_name='Дата выдачи',
    )
    institute = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name='Учебное заведение',
    )

    def __str__(self):
        return '{} - {}'.format(self.profile.full_name,
                                self.institute)

    class Meta:
        verbose_name = 'Образование'
        verbose_name_plural = 'Образования'
        unique_together = (
            'profile',
            'document_type',
            'edu_type',
            'serial_number',
            'number',
        )


class StudyPeriod(BaseModel):
    start = models.PositiveSmallIntegerField(
        verbose_name='Начало',
    )
    end = models.PositiveSmallIntegerField(
        verbose_name='Окончание',
    )
    is_study_year = models.BooleanField(
        default=False,
        verbose_name='Учебный год',
    )

    @property
    def repr_name(self):
        return '{}-{}'.format(self.start,
                              self.end)

    def __str__(self):
        return '{}-{}'.format(self.start,
                              self.end)

    class Meta:
        verbose_name = 'Учебный период'
        verbose_name_plural = 'Учебные периоды'


class StudyYearCourse(BaseModel):
    study_plan = models.ForeignKey(
        'StudyPlan',
        on_delete=models.CASCADE,
        verbose_name='Учебный план',
        related_name='study_year_courses',
    )
    study_year = models.ForeignKey(
        'StudyPeriod',
        on_delete=models.CASCADE,
        verbose_name='Учебный год',
    )
    course = models.PositiveIntegerField(
        verbose_name='Курс',
    )

    def __str__(self):
        return '{} {}'.format(self.study_plan,
                              self.course)

    class Meta:
        verbose_name = 'Учебный Год - Курс'
        verbose_name_plural = 'Учебный Год - Курс'


class StudyPlan(BaseModel):
    number = models.CharField(
        max_length=100,
        null=True,
        verbose_name='Номер',
    )
    uid_1c = models.CharField(
        max_length=100,
        null=True,
        verbose_name='uid 1C',
    )
    student = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Студент',
    )
    advisor = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        null=True,
        related_name='student_study_plans',
        verbose_name='Эдвайзер',
    )
    study_period = models.ForeignKey(
        StudyPeriod,
        on_delete=models.CASCADE,
        verbose_name='Период обучения',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Группа',
    )
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.CASCADE,
        verbose_name='Направление подготовки',
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        verbose_name='Факультет',
    )
    cathedra = models.ForeignKey(
        Cathedra,
        on_delete=models.CASCADE,
        verbose_name='Выпускаюшая кафедра',
    )
    education_program = models.ForeignKey(
        EducationProgram,
        on_delete=models.CASCADE,
        verbose_name='Образовательная программа',
    )
    education_type = models.ForeignKey(
        EducationType,
        related_name='study_plans',
        on_delete=models.CASCADE,
        verbose_name='Вид образования',
    )
    preparation_level = models.ForeignKey(
        PreparationLevel,
        on_delete=models.CASCADE,
        verbose_name='Уровень подготовки',
    )
    study_form = models.ForeignKey(
        StudyForm,
        on_delete=models.CASCADE,
        verbose_name='Форма обучения',
    )
    education_base = models.ForeignKey(
        EducationBase,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Основа обучения',
    )
    on_base = models.ForeignKey(
        EducationType,
        on_delete=models.CASCADE,
        verbose_name='На базе',
    )
    entry_date = models.DateField(
        null=True,
        verbose_name='Дата поступления в ВУЗ',
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.exchange:
            old_items = StudyYearCourse.objects.filter(study_plan=self)
            for i in old_items:
                i.delete()

            study_years = divide_to_study_years(self.study_period)

            for study_year_item in study_years:
                study_year = StudyPeriod.objects.filter(start=study_year_item[0],
                                                        end=study_year_item[1]).first()
                # if study_year is None:
                #     study_year = StudyPeriod.objects.create(start=study_year_item[0],
                #                                             end=study_year_item[1])

                StudyYearCourse.objects.create(
                    study_plan=self,
                    study_year=study_year,
                    course=study_years.index(study_year_item) + 1,
                )

    def __str__(self):
        return 'Уч.план {}'.format(self.number)

    @property
    def current_course(self):
        """Текущий курс студента"""
        return get_current_course(self.study_period)

    def get_course(self, study_year):
        """Возвращает курс студента в указанном учебном году
        Если учебный год вне диапазона периода обучения вернет None"""
        return get_course(self.study_period, study_year)

    class Meta:
        verbose_name = 'Учебный план'
        verbose_name_plural = 'Учебные планы'
        unique_together = (
            'student',
            'uid_1c',
            # 'group',
            # 'education_program',
        )


class Prerequisite(BaseModel):
    study_period = models.ForeignKey(
        StudyPeriod,
        on_delete=models.CASCADE,
        verbose_name='Учебный период',
    )
    discipline = models.ForeignKey(
        'organizations.Discipline',
        on_delete=models.CASCADE,
        verbose_name='Дисциплина',
        related_name='prerequisites',
    )
    required_discipline = models.ForeignKey(
        'organizations.Discipline',
        on_delete=models.CASCADE,
        verbose_name='Требуемая дисциплина',
    )
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.CASCADE,
        verbose_name='Направление подготовки',
    )

    # def save(self, *args, **kwargs):
    #     if self.exchange:
    #         self.uid = uuid4()
    #     super(Prerequisite, self).save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.required_discipline,
                                self.discipline)

    class Meta:
        verbose_name = 'Пререквизит'
        verbose_name_plural = 'Пререквизиты'
        unique_together = (
            'study_period',
            'discipline',
            'required_discipline',
            'speciality',
        )


class Postrequisite(BaseModel):
    study_period = models.ForeignKey(
        StudyPeriod,
        on_delete=models.CASCADE,
        verbose_name='Учебный период',
    )
    discipline = models.ForeignKey(
        'organizations.Discipline',
        on_delete=models.CASCADE,
        verbose_name='Дисциплина',
        related_name='postrequisites',
    )
    available_discipline = models.ForeignKey(
        'organizations.Discipline',
        on_delete=models.CASCADE,
        verbose_name='Доступная дисциплина',
    )
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.CASCADE,
        verbose_name='Направление подготовки',
    )

    # def save(self, *args, **kwargs):
    #     if self.exchange:
    #         self.uid = uuid4()
    #     super(Postrequisite, self).save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.discipline,
                                self.available_discipline)

    class Meta:
        verbose_name = 'Постреквизит'
        verbose_name_plural = 'Постреквизиты'
        unique_together = (
            'study_period',
            'discipline',
            'available_discipline',
            'speciality',
        )


class Discipline(BaseCatalog):
    description = models.TextField(
        verbose_name='Описание',
        default='',
        blank=True,
    )
    is_language = models.BooleanField(
        default=False,
        verbose_name='Языковая дисциплина?'
    )

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'
        # ordering = (
        #     'name',
        # )

    # def save(self, *args, **kwargs):
    #     if self.exchange:
    #         """При выгрузке деактивируем существующие пре и постреквизити"""
    #         for pos_req in Postrequisite.objects.all():
    #             pos_req.is_active = False
    #             pos_req.save()
    #
    #         for pre_req in Prerequisite.objects.all():
    #             pre_req.is_active = False
    #             pre_req.save()
    #
    #     super(Discipline, self).save()


class LoadType2(BaseCatalog):
    number = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Номер',
    )
    uid_1c = models.CharField(
        max_length=200,
        default='',
        verbose_name='УИД 1С',
    )

    # def save(self, *args, **kwargs):
    #     if self.exchange:
    #         self.uid = uuid4()
    #
    #     super(LoadType2, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Тип нагрузки'
        verbose_name_plural = 'Типы нагрузок'
        unique_together = (
            'name_ru',
        )


class LoadType(BaseCatalog):
    load_type2 = models.ForeignKey(
        LoadType2,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Тип нагрузки',
    )
    parent_uid_1c = models.CharField(
        max_length=200,
        default='',
        verbose_name='УИД 1С родителя',
    )

    def save(self, *args, **kwargs):
        if self.exchange:
            if self.parent_uid_1c:  # Находим Тип нагрузки по названию и прикрепим к виду нагрузки
                load_type2 = LoadType2.objects.get(uid_1c=self.parent_uid_1c)
                self.load_type2 = load_type2

        super(LoadType, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Вид нагрузки'
        verbose_name_plural = 'Виды нагрузок'


class AcadPeriodType(BaseCatalog):
    class Meta:
        verbose_name = 'Вид академического периода'
        verbose_name_plural = 'Вид академического периода'


class AcadPeriod(BaseCatalog):
    number = models.IntegerField(
        verbose_name='Номер',
        default=0,
    )
    period_type = models.ForeignKey(
        AcadPeriodType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Вид академического периода',
    )

    def __str__(self):
        return '{} {}'.format(self.number,
                              self.name)

    @property
    def repr_name(self):
        return '{} {}'.format(self.number,
                              self.name)

    class Meta:
        verbose_name = 'Академический период'
        verbose_name_plural = 'Академические периоды'
        ordering = ('number',)


class StudentDisciplineStatus(BaseCatalog):
    number = models.IntegerField(
        null=True,
        verbose_name='Номер',
    )

    class Meta:
        verbose_name = 'Статус при выборе препода'
        verbose_name_plural = 'Статусы при выборе препода'


class StudentDiscipline(BaseModel):
    author = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        related_name='edited_student_disciplines',
        null=True,
        blank=True,
        verbose_name='Автор',
    )
    student = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Студент',
        related_name='student_disciplines',
    )
    study_plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        verbose_name='Учебный план',
    )
    acad_period = models.ForeignKey(
        AcadPeriod,
        on_delete=models.CASCADE,
        verbose_name='Академический период',
    )
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        verbose_name='Дисциплина',
    )
    discipline_code = models.CharField(
        default='',
        max_length=100,
        verbose_name='Код дисциплины',
    )
    load_type = models.ForeignKey(
        LoadType,
        on_delete=models.CASCADE,
        verbose_name='Вид нагрузки',
    )
    hours = models.FloatField(
        verbose_name='Часы',
    )
    teacher = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Преподаватель',
    )
    language = models.ForeignKey(
        Language,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Язык',
    )
    cycle = models.ForeignKey(
        DisciplineCycle,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Цикл дисциплины',
        related_name='student_disciplines',
    )
    component = models.ForeignKey(
        DisciplineComponent,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Компонент дисциплины',
        related_name='student_disciplines',
    )
    status = models.ForeignKey(
        StudentDisciplineStatus,
        on_delete=models.CASCADE,
        # default=curr_settings.student_discipline_status['not_chosen'],
        null=True,
        verbose_name='Статус',
    )
    study_year = models.ForeignKey(
        StudyPeriod,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Учебный год',
    )
    study_plan_uid_1c = models.CharField(
        max_length=100,
        null=True,
        verbose_name='uid 1c учебного плана',
    )
    sent = models.BooleanField(
        default=False,
        verbose_name='Отправлен в 1С',
    )
    uid_1c = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name='УИД документа-аналога в 1С',
        help_text='придет, после выгрузки в 1С',
    )

    def save(self, *args, **kwargs):
        if self.exchange:
            if self._state.adding:
                self.status_id = curr_settings.student_discipline_status['not_chosen']

            try:
                study_plan = StudyPlan.objects.get(student=self.student,
                                                   uid_1c=self.study_plan_uid_1c)
                self.study_plan = study_plan
            except StudyPlan.DoesNotExist:
                print('StudyPlan not found')

        super(StudentDiscipline, self).save(*args, **kwargs)

    @property
    def credit(self):
        """Возвращает кредит дисциплины"""
        return calculate_credit(self.discipline,
                                self.student,
                                self.acad_period)

    def __str__(self):
        return '{} {}'.format(self.acad_period,
                              self.discipline)

    class Meta:
        verbose_name = 'Дисциплина студента'
        verbose_name_plural = 'Дисциплины студента'
        unique_together = (
            'student',
            'study_plan_uid_1c',
            'acad_period',
            'discipline_code',
            'discipline',
            'load_type',
            'hours',
            'language',
            'cycle',
            'study_year',
        )


class StudentDisciplineInfoStatus(BaseCatalog):
    number = models.IntegerField(
        null=True,
        verbose_name='Номер',
    )

    class Meta:
        verbose_name = 'Статус об общем выборе препода'
        verbose_name_plural = 'Статус об общем выборе препода'


class StudentDisciplineInfo(BaseModel):
    student = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Студент',
    )
    study_plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        verbose_name='Учебный план',
    )
    acad_period = models.ForeignKey(
        AcadPeriod,
        on_delete=models.CASCADE,
        verbose_name='Академический период',
    )
    status = models.ForeignKey(
        StudentDisciplineInfoStatus,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Статус',
    )

    def __str__(self):
        return "{} {}".format(self.student,
                              self.acad_period)

    class Meta:
        verbose_name = 'Инфо о выборе студента'
        verbose_name_plural = 'Инфо о выбора студента'
        unique_together = (
            'acad_period',
            'study_plan',
        )


class TeacherDiscipline(BaseModel):
    teacher = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Преподаватель',
    )
    study_period = models.ForeignKey(
        StudyPeriod,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Учебный период',
    )
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        verbose_name='Дисциплина',
    )
    load_type2 = models.ForeignKey(
        LoadType2,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Тип нагрузки',
    )
    load_type2_uid_1c = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='УИД 1С Типа нагрузки',
    )
    language = models.ForeignKey(
        Language,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Язык преподавания',
    )

    def save(self, *args, **kwargs):
        if self.exchange:
            """Находим Тип нагрузки по названию и прикрепим к виду нагрузки"""
            if self.load_type2_uid_1c:
                try:
                    load_type2 = LoadType2.objects.get(uid_1c=self.load_type2_uid_1c)
                    self.load_type2 = load_type2
                except LoadType2.DoesNotExist:
                    print('LoadType2 not found')

        super(TeacherDiscipline, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {}'.format(self.teacher.user.get_full_name(),
                              self.discipline)

    class Meta:
        verbose_name = 'Закрепление дисциплин'
        verbose_name_plural = 'Закрепление дисциплин'
        unique_together = (
            'teacher',
            'study_period',
            'discipline',
            'load_type2_uid_1c',
            'language',
        )
