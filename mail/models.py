import re
from django.db import models
from django.template import Template, Context
from common.models import BaseModel, InstitutionConfig
from cron_app.models import EmailTask


class EmailTemplate(BaseModel):
    config = models.ForeignKey(
        InstitutionConfig,
        on_delete=models.PROTECT,
        verbose_name='Настройка ОУ',
        related_name='email_templates',
        blank=True,
        null=True
    )
    type = models.CharField(
        max_length=255,
        verbose_name='Тип шаблона',
        blank=True,
        null=True,
        unique=True,
        editable=False,
    )
    subject = models.CharField(
        max_length=255,
        verbose_name='Тема письма'
    )
    template = models.TextField(
        verbose_name='Шаблон письма',
        blank=True,
        null=True
    )
    is_dynamic = models.BooleanField(
        default=True,
        verbose_name='Шаблон динамический?',
    )

    class Meta:
        verbose_name = 'Шаблон письма'
        verbose_name_plural = 'Шаблоны писем'
        unique_together = ['config', 'type']

    def __str__(self):
        return self.subject

    def get_variables(self):
        """Если шаблон динамический (т.е. в нем есть переменные, которые меняются от юзера к юзеру) кстати
        эти переменные должны быть закрыты в таких скобках {{
        """
        if self.is_dynamic and self.template:
            regex = r'\{\{.*?\}\}'
            matches = re.findall(regex, self.template)
            if len(matches) == 0:
                return
            variables = list({variable.replace('{{', '').replace('}}', '').strip() for variable in matches})
            return variables
        return

    def build_template(self, **kwargs):
        """На основе шаблона и предоставленных данных (kwargs)
         создается письмо, которое потом отправится по крону
         """
        variables = self.get_variables()
        if not variables:
            return self.template
        missing_vars = [variable for variable in variables if variable not in kwargs]
        if missing_vars:
            msg = f'Не хватает переменных для заполнения шаблона: {", ".join(missing_vars)}'
            raise AttributeError(msg)
        template = Template(self.template)
        context = Context(kwargs)
        result = template.render(context)
        return result

    @staticmethod
    def put_in_cron_queue(template_type: str, recipient: str, **kwargs: dict):
        """Отрисованный динамическйи шаблон/простой шаблон отправляется в крон"""
        template: EmailTemplate = EmailTemplate.objects.get(type=template_type)
        message = template.build_template(**kwargs)
        email_task = EmailTask.objects.create(
            subject=template.subject,
            message=message,
            to=recipient
        )
        return email_task
