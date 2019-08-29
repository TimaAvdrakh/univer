from django.db import models
from common.models import BaseModel
from portal_users.models import ResetPassword


class BaseTask(BaseModel):
    is_success = models.BooleanField(
        default=False,
        verbose_name='Успешно',
    )

    class Meta:
        abstract = True


class EmailTask(BaseTask):
    """Задача для отправки email"""
    to = models.EmailField(
        verbose_name='Email',
    )
    subject = models.CharField(
        max_length=50,
        null=True,
        verbose_name='Заголовок',
    )
    message = models.CharField(
        max_length=100,
        null=True,
        verbose_name='Сообщение',
    )


class ResetPasswordUrlSendTask(BaseTask):
    """Задача для отправки ссылки для восстановления пароля"""
    reset_password = models.ForeignKey(
        ResetPassword,
        on_delete=models.CASCADE,
    )


class CredentialsEmailTask(BaseTask):
    """Задача для отправки логин и пароль на email"""
    to = models.EmailField(
        verbose_name='Email',
    )
    username = models.CharField(
        max_length=50,
        verbose_name='Логин',
    )
    password = models.CharField(
        max_length=100,
        verbose_name='Пароль',
    )
