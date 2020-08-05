from typing import List
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.timezone import now
from common.models import BaseModel
from portal_users.models import Role, Profile
from organizations.models import Faculty, Cathedra, EducationProgram, PreparationLevel

User = get_user_model()


class News(BaseModel):
    title = models.CharField(
        max_length=1000,
        verbose_name='Заголовок'
    )
    content = models.TextField(verbose_name='Контент')
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='news',
        verbose_name='Автор новости'
    )
    is_important = models.BooleanField(
        default=False,
        verbose_name='Важная новость?'
    )
    files = models.ManyToManyField(
        'common.File',
        blank=True,
        verbose_name='Прикрепленные файлы'
    )
    addressees = models.ManyToManyField(
        'portal_users.Profile',
        blank=True,
        verbose_name='Адресаты'
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        default=now,
        blank=True,
    )
    roles = ArrayField(
        base_field=models.CharField(max_length=100),
        blank=True,
        null=True,
        verbose_name='Типы ролей'
    )
    courses = ArrayField(
        base_field=models.PositiveSmallIntegerField(),
        blank=True,
        null=True,
        verbose_name='Курсы'
    )
    prep_levels = models.ManyToManyField(
        PreparationLevel,
        blank=True,
        verbose_name='Уровни образования'
    )
    faculties = models.ManyToManyField(
        Faculty,
        blank=True,
        verbose_name='Факультеты'
    )
    cathedras = models.ManyToManyField(
        Cathedra,
        blank=True,
        verbose_name='Кафедры'
    )
    education_programs = models.ManyToManyField(
        EducationProgram,
        blank=True,
        verbose_name='Обр. программы'
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        verbose_name='Группы'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.title[:30]}, Автор {self.author}'

    def set_for(
            self,
            role_types: List[str] = None,
            addressees: List[Profile] = None,
            courses: List[int] = None,
            prep_levels: List[PreparationLevel] = None,
            faculties: List[Faculty] = None,
            cathedras: List[Cathedra] = None,
            education_programs: List[EducationProgram] = None,
            groups: List[Group] = None
    ):
        if role_types:
            origin_role_types = set(Role.get_role_types())
            role_types = set(role_types)
            assert role_types.issubset(origin_role_types), "Given role types are not a subset of original role types"
            self.roles = list(role_types)
        if courses:
            self.courses = courses
        if addressees:
            self.addressees = addressees
        if prep_levels:
            self.prep_levels = prep_levels
        if faculties:
            self.faculties = faculties
        if cathedras:
            self.cathedras = cathedras
        if education_programs:
            self.education_programs = education_programs
        if groups:
            self.groups = groups
        self.save()
        return
