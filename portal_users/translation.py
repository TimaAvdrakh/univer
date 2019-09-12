from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.Gender)
class GenderTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.MaritalStatus)
class MaritalStatusTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Level)
class LevelTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.AchievementType)
class AchievementTypeTranslationOptions(TranslationOptions):
    fields = ('name',)
