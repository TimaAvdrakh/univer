import sys

from django.db import models
from django.utils.translation import ugettext as _
from common.models import BaseModel, BaseCatalog, BaseIdModel
#from django.utils import timezone
from django.contrib.postgres.fields import ArrayField



# Сканы документов
class Example(models.Model):
    file = models.FileField(
        verbose_name=_("File"),
        upload_to="media"
    )
    path = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Path to file")
    )
    ext = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("File extension")
    )
    name = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("File name")
    )
    size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("File size")
    )
    # File's content type not Django's
    content_type = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("Content type of a file")
    )

    def __str__(self):
        if self.name:
            return self.name
        else:
            return super().__str__()

    class Meta:
        verbose_name = _("Example")

class IdentityDoc(Example):
    class Meta:
        verbose_name = _("Identity document")

class ServiceDoc(Example):
    class Meta:
        verbose_name = _("Service virtual document")

class Type(BaseCatalog):
    class Meta:
        verbose_name = 'Тип заявки'
        verbose_name_plural = 'Типы заявок'

class Status(BaseCatalog):
    c1_id = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name='Ид в 1с',
    )

    class Meta:
        verbose_name = 'Статус заявки'
        verbose_name_plural = 'Статусы заявок'
# DEFAULT_STATUS = Status.objects.get(c1_id="1")


class SubType(BaseCatalog):
    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        verbose_name=_("Type"),
        blank=True,
        null=True,
    )

    example = models.ForeignKey(
        Example,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Document example"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Вид справки'
        verbose_name_plural = 'Виды справок'

class Application(BaseIdModel):
    profile = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Профиль',
        related_name='students_profile'
    )

    type = models.ForeignKey(
        Type,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    identity_doc = models.ForeignKey(
        IdentityDoc,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Identity document")
    )

    send = models.BooleanField(
        default=False,
        verbose_name=_("Is send to 1C")
    )

    def __str__(self):
        return '{}) {} - {} {}'.format(self.id,
                self.type.name, self.profile.last_name, self.profile.first_name)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

class SubApplication(BaseIdModel):
    subtype = models.ForeignKey(
        SubType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    organization = models.TextField(
        default='',
        null=True,
    )

    lang = ArrayField(
        models.CharField(max_length=20, blank=True),
        size=3,
        default=list,
        verbose_name='Языки',
    )

    is_paper = models.BooleanField(
        default=True,
        verbose_name='Бумажный вариант',
    )

    copies = models.PositiveSmallIntegerField(
        verbose_name=_("Copies"),
        blank=True,
        null=True,
        default=1,
    )

    responsible = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='Ответственный специалист',
    )

    result_doc = models.ForeignKey(
        ServiceDoc,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Result document")
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Status"),
        null=True,
        # default=DEFAULT_STATUS
    )

    comment = models.TextField(
        default='',
        null=True,
        blank=True,
        verbose_name='Комментарий к статусу'
    )

    class Meta:
        verbose_name = 'Справка'
        verbose_name_plural = 'Справки'
