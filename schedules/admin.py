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
    search_fields = (
        'name',
        'from_time',
        'to_time',
    )
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
    search_fields = (
        'subject',
        'discipline__name',
    )
    autocomplete_fields = (
        'discipline',
        'acad_period',
        'study_year',
        'time',
        'teachers',
    )
    list_filter = (
        'date',
        'time',
        'el_journal',
    )
    list_display = (
        'discipline',
        'subject',
        'date',
        'time',
        'uid',
        'acad_period',
        'study_year',
        'status',
    )


@admin.register(models.Mark)
class MarkAdmin(admin.ModelAdmin):
    search_fields = (
        'weight',
        'value_traditional',
        'value_letter',
        'value_number',
    )
    list_display = (
        'weight',
        'grading_system',
        'value_letter',
        'value_number',
        'value_traditional',
    )


@admin.register(models.StudentPerformance)
class StudentPerformanceAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'lesson',
        'student',
        'mark',
    )
    list_display = (
        'lesson',
        'student',
        'mark',
        'missed',
        'reason',
    )


# @admin.register(models.JournalStatus)
# class JournalStatusAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'uid',
#     )


@admin.register(models.ElectronicJournal)
class ElectronicJournalAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'discipline',
        'load_type',
    )
    list_display = (
        'discipline',
        'load_type',
        'closed',
    )


@admin.register(models.LessonTeacher)
class LessonTeacherAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'teacher',
    )
    list_display = (
        'flow_uid',
        'teacher',
        'is_active',
    )


@admin.register(models.LessonStudent)
class LessonTeacherAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'group',
        'parent_group',
        'student',
    )
    list_display = (
        'flow_uid',
        'group_identificator',
        'group',
        'parent_group',
        'is_subgroup',
        'student',
        'is_active',
    )
