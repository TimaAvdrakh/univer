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
    uid_1c = models.CharField(
        max_length=100,
        null=True,
        verbose_name='uid 1C',
    )
    acad_period = models.ForeignKey(
        'organizations.AcadPeriod',
        on_delete=models.CASCADE,
        verbose_name='Академический период')
    student = models.ForeignKey(
        user_models.Profile,
        null=True,
        on_delete=models.SET_NULL,
        related_name='student_themes_theses',
        verbose_name='Обучающийся',
        blank=True
    )
    supervisors = models.ManyToManyField(
        user_models.Profile,
        related_name='supervisors_themes_theses',
        verbose_name='Руководители')
    supervisor_leader = models.TextField(
        verbose_name='Руководитель извне',
        null=True,
        blank=True)
    uid_1c = models.CharField(
        max_length=100,
        null=True,
        default='',
        blank=True,
        verbose_name='УИД документа-аналога в 1С',
        help_text='придет, после выгрузки в 1С',
    )
    sent = models.NullBooleanField(
        default=False,
        verbose_name='Отправлен в 1С',
    )

    def __str__(self):
        return '{} - {}'.format(self.student, self.acad_period)

    @property
    def supervisors_text(self):
        text = ""
        for x in self.supervisors.all():
            text += '{} {} {}, '.format(x.last_name, x.first_name, x.middle_name)
        return text[0:-2]

    class Meta:
        unique_together = [['uid_1c', 'student']]
        verbose_name = 'Тема дипломной работы'
        verbose_name_plural = 'Темы дипломных работ'
