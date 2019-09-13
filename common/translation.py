from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.RegistrationPeriod)
class RegistrationForDisciplineTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.GovernmentAgency)
class GosOrganizationTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.DocumentType)
class DocumentTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Nationality)
class NationalityTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Citizenship)
class CitizenshipTranslationOptions(TranslationOptions):
    fields = ('name',)
