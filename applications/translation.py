from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(Type)
class TypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(SubType)
class SubTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Status)
class StatusTranslationOptions(TranslationOptions):
    fields = ('name',)
