from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.RegistrationPeriod)
class RegistrationForDisciplineTranslationOptions(TranslationOptions):
    fields = ('name',)
