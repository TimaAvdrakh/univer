from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.Organization)
class OrganizationTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.StudyForm)
class StudyFormTranslationOptions(TranslationOptions):
    fields = ('name',)

