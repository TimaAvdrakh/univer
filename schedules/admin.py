from django.contrib import admin
from . import models


@admin.register(models.RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uid',
    )


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uid',
        # 'department',
        'type',
        'capacity',
    )


@admin.register(models.TimeWindow)
class TimeWindowAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'from_time',
        'to_time',
        'uid',
    )


@admin.register(models.GradingSystem)
class GradingSystemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uid',
    )


@admin.register(models.LessonStatus)
class LessonStatusAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uid',
    )


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'discipline',
        'subject',
        'uid',
        'acad_period',
        'study_year',
        'status',
    )


@admin.register(models.Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = (
        'weight',
        'grading_system',
        'value_letter',
        'value_number',
        'value_traditional',
    )


@admin.register(models.StudentPerformance)
class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        'lesson',
        'student',
        'mark',
        'missed',
        'reason',
    )
