from django.db import models
from common.models import BaseModel, BaseCatalog, DocumentType
from django.contrib.auth.models import User
from common.utils import get_sentinel_user


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
    class Meta:
        verbose_name = 'Кафедра'
        verbose_name_plural = 'Кафедры'


# class Group(BaseCatalog):
#     year = models.CharField(
#         verbose_name='Год',
#     )
#     students = models.ManyToManyField(
#         User,
#         blank=True,
#         verbose_name='Студенты',
#     )
#     headman = models.OneToOneField(
#         User,
#         on_delete=models.SET(get_sentinel_user),
#         related_name='',
#         verbose_name='Староста',
#     )
#     kurator = models.ForeignKey(
#         User,
#         on_delete=models.SET(get_sentinel_user),
#         verbose_name='Куратор',
#         related_name='groups',
#     )
#     supervisor = models.ForeignKey(
#         User,
#         on_delete=models.SET(get_sentinel_user),
#         verbose_name='Супервизор',
#     )
#
#     def __str__(self):
#         return '{} - {}'.format(self.name,
#                                 self.year)
#
#     class Meta:
#         verbose_name = 'Группа'
#         verbose_name_plural = 'Группы'


class EducationBase(BaseCatalog):
    class Meta:
        verbose_name = 'Основа обучения'
        verbose_name_plural = 'Основы обучения'


# class PreparationDirection(BaseCatalog):
#     class Meta:
#         verbose_name = 'Направление подготовки'
#         verbose_name_plural = 'Направления подготовки'


class PreparationLevel(BaseCatalog):
    class Meta:
        verbose_name = 'Уровень подготовки'
        verbose_name_plural = 'Уровни подготовок'


class EducationProgram(BaseCatalog):
    class Meta:
        verbose_name = 'Образовательная программа'
        verbose_name_plural = 'Образовательные программы'


class EducationType(BaseCatalog):
    class Meta:
        verbose_name = 'Вид образования'
        verbose_name_plural = 'Виды образования'


class Education(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.SET(get_sentinel_user),
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
        return '{} - {}'.format(self.user.username,
                                self.institute)

    class Meta:
        verbose_name = 'Образование'
        verbose_name_plural = 'Образования'
