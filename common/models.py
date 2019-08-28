from django.db import models
from django.contrib.auth.models import User
from .utils import get_sentinel_user
from django.contrib.postgres.fields import JSONField
from uuid import uuid4


class BaseModel(models.Model):
    class Meta:
        abstract = True

    uid = models.UUIDField(
        verbose_name='Уникальный идентификатор',
        primary_key=True,
        editable=False,
        default=uuid4,
        unique=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    deleted = models.DateTimeField(
        null=True,
        blank=True,
    )


# class Log(BaseModel):
#     obj_uid = models.CharField()
#     model_name = models.CharField()
#     author = models.ForeignKey(
#         User,
#         on_delete=models.SET(get_sentinel_user),
#         verbose_name='Автор',
#         related_name='my_actions',
#     )
#     date = models.DateTimeField(
#         auto_now_add=True,
#     )
#     content = JSONField(
#         verbose_name='Контент',
#     )
#
#     def __str__(self):
#         return '{} - {}'.format(self.obj_uid, self.author.username)
#
#     class Meta:
#         verbose_name = 'Лог'
#         verbose_name_plural = 'Логи'
