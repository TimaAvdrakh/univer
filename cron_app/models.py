from django.db import models
from common.models import BaseModel


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
        'portal_users.ResetPassword',
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


class StudPerformanceChangedTask(BaseTask):
    """Задача для уведомления админов об изменении оценки"""
    author = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    stud_perf = models.ForeignKey(
        'schedules.StudentPerformance',
        on_delete=models.CASCADE,
        verbose_name='Успеваемость студента',
    )
    old_mark = models.ForeignKey(
        'schedules.Mark',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Старая оценка',
    )
    new_mark = models.ForeignKey(
        'schedules.Mark',
        on_delete=models.CASCADE,
        verbose_name='Новая оценка',
    )


class ControlNotifyTask(BaseTask):
    """Задача для уведомления студентов о промежуточном контроле"""
    lesson = models.ForeignKey(
        'schedules.Lesson',
        on_delete=models.CASCADE,
        verbose_name='Занятие',
    )


class PlanCloseJournalTask(BaseTask):
    """Задача для блокировки Журналов в запланированное время"""
    date_time = models.DateTimeField(
        verbose_name='Дата время блокировки',
    )
    journals = models.ManyToManyField(
        'schedules.ElectronicJournal',
        verbose_name='Журналы',
    )


class ExcelTask(BaseTask):
    DOC_TYPE_CHOICES = (
        (1, 'Результат регистрации'),
        (2, 'Статистика регистрации '),
        (3, 'Список незарегистрированных'),
    )
    doc_type = models.IntegerField(
        choices=DOC_TYPE_CHOICES,
        verbose_name='Тип документа',
    )
    token = models.UUIDField(
        verbose_name='Токен',
    )
    fields = models.TextField(
        verbose_name='Поля',
    )
    profile = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Профиль',
    )
    file_path = models.CharField(
        default='',
        max_length=1000,
    )

    class Meta:
        verbose_name = 'Ексель файлы'
        verbose_name_plural = 'Ексель файлов'


