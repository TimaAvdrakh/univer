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
        verbose_name = _("Scan of document")
        verbose_name_plural = _("Scans of documents")

class IdentityDoc(Example):
    class Meta:
        verbose_name = _("Scan of document")
        verbose_name_plural = _("Scans of documents")

# Create your models here.
class Type(BaseCatalog):
        class Meta:
            verbose_name = 'Тип заявки'
            verbose_name_plural = 'Типы заявок'

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

class Service(BaseIdModel):
        type = models.ForeignKey(
            Type,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
        )

        identity_doc = models.ForeignKey(
            IdentityDoc,
            on_delete=models.DO_NOTHING,
            verbose_name=_("Identity Document")
        )

        class Meta:
            verbose_name = 'Заявка'
            verbose_name_plural = 'Заявки'

class SubService(BaseIdModel):
        subtype = models.ForeignKey(
            SubType,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
        )

        service = models.ForeignKey(
            Service,
            on_delete=models.CASCADE,
            blank=True,
            null=True,
        )

        organization = models.CharField(
            max_length=500,
            default='',
            blank=True,
            verbose_name='Наименование организации',
        )

        lang = models.CharField(
            max_length=5,
            default='',
            blank=True,
            verbose_name='Язык',
        )

        # вид документа электронный/бумажный
        # инт для количества копий

        class Meta:
            verbose_name = 'Справка'
            verbose_name_plural = 'Справки'