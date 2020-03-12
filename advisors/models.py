from django.db import models
from common.models import BaseIdModel, BaseCatalog
from organizations import models as org_models
from portal_users import models as user_models


class AdvisorCheck(BaseIdModel):
    STATUS_CHOICES = (
        (3, 'Отклонено'),
        (4, 'Утверждено'),
        (5, 'Изменено'),
    )

    study_plan = models.ForeignKey(
        'organizations.StudyPlan',
        on_delete=models.CASCADE,
    )
    acad_period = models.ForeignKey(
        'organizations.AcadPeriod',
        on_delete=models.CASCADE,
        null=True,
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
    )
    comment = models.TextField(
        default='',
        null=True,
    )

    def __str__(self):
        return '{} - {}'.format(self.study_plan,
                                self.status)

    class Meta:
        verbose_name = 'Метка Эдвайзера'
        verbose_name_plural = 'Метки Эдвайзера'


class ThemesOfTheses(BaseCatalog):
    study_plan = models.ForeignKey(
        org_models.StudyPlan,
        on_delete=models.CASCADE,
        verbose_name='Учебный план')
    acad_period = models.ForeignKey(
        'organizations.AcadPeriod',
        on_delete=models.CASCADE,
        verbose_name='Академический период')
    student = models.ForeignKey(
        user_models.Profile,
        null=True,
        on_delete=models.SET_NULL,
        related_name='student_themes_theses',
        verbose_name='Обучающийся')
    supervisors = models.ManyToManyField(
        user_models.Profile,
        related_name='supervisors_themes_theses',
        verbose_name='Руководители')
    supervisor_leader = models.CharField(
        verbose_name='Руководитель извне',
        max_length=1000,
        null=True,
        blank=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.student, self.study_plan, self.acad_period)

    class Meta:
        verbose_name = 'Тема дипломной работы'
        verbose_name_plural = 'Темы дипломных работ'
