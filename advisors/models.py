from django.db import models
from common.models import BaseIdModel


class AdvisorCheck(BaseIdModel):
    STATUS_CHOICES = (
        (3, 'Отклонено'),
        (4, 'Утверждено'),
        # ()
    )

    study_plan = models.ForeignKey(
        'organizations.StudyPlan',
        on_delete=models.CASCADE,
    )
    acad_periods = models.ManyToManyField(
        'organizations.AcadPeriod',
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
