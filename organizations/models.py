from django.db import models
from common.models import BaseModel, BaseCatalog, DocumentType
from django.contrib.auth.models import User
from common.utils import get_sentinel_user
from portal import curr_settings
from datetime import date
from portal_users.utils import get_current_study_year, get_current_course, get_course


class Language(BaseCatalog):
    class Meta:
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'


class Organization(BaseCatalog):
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'


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
        on_delete=models.CASCADE,
        related_name='my_groups',
        verbose_name='Староста',
    )
    kurator = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Куратор',
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Язык обучения',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Student(BaseModel):
    profile = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Профиль',
        related_name='students',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name='Группа',
        related_name='students',
    )

    def __str__(self):
        return '{}'.format(self.profile,
                           self.group)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'


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


class StudyPeriod(BaseModel):
    start = models.PositiveSmallIntegerField(
        verbose_name='Начало',
    )
    end = models.PositiveSmallIntegerField(
        verbose_name='Окончание',
    )

    def __str__(self):
        return '{}-{}'.format(self.start,
                              self.end)

    class Meta:
        verbose_name = 'Учебный период'
        verbose_name_plural = 'Учебные периоды'


class StudyPlan(BaseModel):
    number = models.CharField(
        max_length=100,
        null=True,
        verbose_name='Номер',
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

    def __str__(self):
        return 'Уч.план {}-{}-{}'.format(self.student.first_name,
                                         self.speciality,
                                         self.group.name)

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


class LoadType2(BaseCatalog):
    class Meta:
        verbose_name = 'Тип нагрузки'
        verbose_name_plural = 'Типы нагрузок'


class LoadType(BaseCatalog):
    load_type2 = models.ForeignKey(
        LoadType2,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Тип нагрузки',
    )

    class Meta:
        verbose_name = 'Вид нагрузки'
        verbose_name_plural = 'Виды нагрузок'


class AcadPeriodType(BaseCatalog):
    class Meta:
        verbose_name = 'Вид академического периода'
        verbose_name_plural = 'Вид академического периода'


class AcadPeriod(BaseCatalog):
    period_type = models.ForeignKey(
        AcadPeriodType,
        on_delete=models.CASCADE,
        verbose_name='Вид академического периода',
    )

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = 'Академический период'
        verbose_name_plural = 'Академические периоды'


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
    # study_year = models.ForeignKey(
    #     StudyPeriod,
    #     on_delete=models.CASCADE,
    #     null=True,
    #     verbose_name='Учебный год',
    # )
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
    status = models.ForeignKey(
        StudentDisciplineStatus,
        on_delete=models.CASCADE,
        # default=curr_settings.student_discipline_status['not_chosen'],
        null=True,
        verbose_name='Статус',
    )

    def __str__(self):
        return '{} {}'.format(self.acad_period,
                              self.discipline)

    class Meta:
        verbose_name = 'Дисциплина студента'
        verbose_name_plural = 'Дисциплины студента'


class StudentDisciplineInfoStatus(BaseCatalog):
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
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        verbose_name='Язык преподавания',
    )

    def __str__(self):
        return '{} {}'.format(self.teacher.user.get_full_name(),
                              self.discipline)

    class Meta:
        verbose_name = 'Закрепление дисциплин'
        verbose_name_plural = 'Закрепление дисциплин'


class Prerequisite(BaseModel):
    study_period = models.ForeignKey(
        StudyPeriod,
        on_delete=models.CASCADE,
        verbose_name='Учебный период',
    )
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        verbose_name='Дисциплина',
        related_name='prerequisites',
    )
    required_discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        verbose_name='Требуемая дисциплина',
    )
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.CASCADE,
        verbose_name='Направление подготовки',
    )

    def __str__(self):
        return '{} - {}'.format(self.required_discipline,
                                self.discipline)

    class Meta:
        verbose_name = 'Пререквизит'
        verbose_name_plural = 'Пререквизиты'


class Postrequisite(BaseModel):
    study_period = models.ForeignKey(
        StudyPeriod,
        on_delete=models.CASCADE,
        verbose_name='Учебный период',
    )
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        verbose_name='Дисциплина',
        related_name='postrequisites',
    )
    available_discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        verbose_name='Доступная дисциплина',
    )
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.CASCADE,
        verbose_name='Направление подготовки',
    )

    def __str__(self):
        return '{} - {}'.format(self.discipline,
                                self.available_discipline)

    class Meta:
        verbose_name = 'Постреквизит'
        verbose_name_plural = 'Постреквизиты'
