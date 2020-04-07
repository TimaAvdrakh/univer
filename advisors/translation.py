from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.ThemesOfTheses)
class ThemesOfThesesTranslationOptions(TranslationOptions):
    fields = ('name',)
