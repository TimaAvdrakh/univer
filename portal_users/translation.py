from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.Gender)
class GenderTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.MaritalStatus)
class MaritalStatusTranslationOptions(TranslationOptions):
    fields = ('name',)
