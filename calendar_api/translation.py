from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(RepetitionTypes)
class RepetitionTypesNameTranslationOptions(TranslationOptions):
    fields = ('name', )