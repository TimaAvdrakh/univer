from django.db import models
from django.utils.translation import ugettext as _
from common.models import BaseModel, BaseCatalog, BaseIdModel


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
            verbose_name=_("Document example")
        )

        class Meta:
            verbose_name = 'Вид справки'
            verbose_name_plural = 'Виды справок'

class Application(BaseIdModel):
        profile = models.ForeignKey(
            'portal_users.Profile',
            on_delete=models.CASCADE,
            verbose_name='Профиль',
            related_name='student_profile'
        )

        type = models.ForeignKey(
            Type,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
        )

        status = models.ForeignKey(
            Status,
            on_delete=models.DO_NOTHING,
            verbose_name=_("Status")
        )

        comment = models.TextField(
            default='',
            null=True,
        )

        responsible = models.CharField(
            max_length=200,
            default='',
            blank=True,
            verbose_name='Ответственный специалист',
        )

        identity_doc = models.ForeignKey(
            IdentityDoc,
            on_delete=models.DO_NOTHING,
            verbose_name=_("Identity document")
        )

        result_doc = models.ForeignKey(
            ServiceDoc,
            on_delete=models.DO_NOTHING,
            verbose_name=_("Result document")
        )

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

        lang = models.CharField(
            max_length=5,
            default='',
            blank=True,
            verbose_name='Язык',
        )

        virtual = models.BooleanField(
            default=False,
            verbose_name='Электронный вариант',
        )

        copies = models.PositiveSmallIntegerField(
            verbose_name=_("Copies"),
            blank=True,
            null=True,
            default=1,
        )

        class Meta:
            verbose_name = 'Справка'
            verbose_name_plural = 'Справки'