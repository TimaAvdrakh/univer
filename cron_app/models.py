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
    lang_code = models.CharField(
        max_length=10,
        verbose_name='Код языка',
        default='ru',
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


class NotifyAdvisorTask(BaseTask):
    """Задача для отправки уведомление Эдвайзеру,
    о завершении выбора студента
    """
    stud_discipline_info = models.ForeignKey(
        'organizations.StudentDisciplineInfo',
        on_delete=models.CASCADE,
        verbose_name='Инфо о выборе студента',
    )


class AdvisorRejectedBidTask(BaseTask):
    """Эдвайзер отклонил заявку студента на регистрацию на дисциплины"""
    study_plan = models.ForeignKey(
        'organizations.StudyPlan',
        on_delete=models.CASCADE,
        verbose_name='Учебный план',
    )
    comment = models.CharField(
        max_length=500,
        verbose_name='Комментарий',
    )
