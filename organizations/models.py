from django.db import models
from common.models import BaseModel
from django.contrib.auth.models import User
from common.utils import get_sentinel_user


class Organization(BaseModel):
    name = models.CharField(
        max_length=500,
        verbose_name='Название',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'


class StudyForm(BaseModel):
    name = models.CharField(
        max_length=500,
        verbose_name='Название',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Форма обучения'
        verbose_name_plural = 'Формы обучения'


#
#
# class Faculty(BaseModel):
#     pass
#
#
# class Cathedra(BaseModel):
#     pass
#
#
# class Group(BaseModel):
#     name = models.CharField(
#         verbose_name='Название группы',
#     )
#     year = models.CharField(
#         verbose_name='Год',
#     )
#     students = models.ManyToManyField(
#         User,
#     )
#     headman = models.ForeignKey(
#         User,
#         on_delete=models.SET(get_sentinel_user),
#         verbose_name='Староста',
#     )
#     kurator = models.ForeignKey(
#         User,
#         on_delete=models.SET(get_sentinel_user)
#     )
#     supervisor = models.ForeignKey(
#         User,
#         on_delete=models.SET(get_sentinel_user),
#     )
#
#     def __str__(self):
#         return '{} - {}'.format(self.name,
#                                 self.year)
#
#     class Meta:
#         verbose_name = 'Группа'
#         verbose_name_plural = 'Группы'


# class Education(BaseModel):  # TODO
#     user = models.ForeignKey(
#         User,
#         on_delete=models.SET(get_sentinel_user),
#         related_name='educations',
#         verbose_name='Пользователь',
#     )
#     document_type = models.CharField()
#     edu_type = models.CharField()
#     serial = models.CharField(
#         verbose_name='Серия',
#     )
#     number = models.IntegerField(
#         verbose_name='Номер',
#     )
#     get_date = models.DateField(
#         verbose_name='Дата выдачи',
#     )
#     institute = models.CharField(
#         verbose_name='Учебное заведение',
#     )
#
#     def __str__(self):
#         return '{} - {}'.format(self.user.username,
#                                 self.institute)
#
#     class Meta:
#         verbose_name = 'Образование'
#         verbose_name_plural = 'Образования'
