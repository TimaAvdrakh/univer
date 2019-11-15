from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.RoomType)
class RoomTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Room)
class RoomTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.TimeWindow)
class TimeWindowTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.GradingSystem)
class GradingSystemTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.LessonStatus)
class LessonStatusTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Lesson)
class LessonTranslationOptions(TranslationOptions):
    fields = ('subject',)
