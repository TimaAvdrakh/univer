from django.db import models
from common.models import BaseModel, BaseCatalog
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class DocumentChangeLog(BaseModel):
    STATUS_CHOICES = (
        (0, 'Данные были успешно загружены'),
        (1, 'Данные не были загружены'),
        (2, 'Данные были загружены с ошибками'),
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.UUIDField(null=True)
    document = GenericForeignKey(
        'content_type',
        'object_id',
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        verbose_name='Статус обмена',
    )
    errors = models.TextField(
        # max_length=1000,
        default='',
        blank=True,
        verbose_name='Ошибки',
    )

    def __str__(self):
        return '{}'.format(self.document)

    class Meta:
        verbose_name = 'Лог обмена документами'
        verbose_name_plural = 'Логи обмена документами'


