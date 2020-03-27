from django.contrib import admin
from . import models


@admin.register(models.AdvisorCheck)
class AdvisorCheckAdmin(admin.ModelAdmin):
    list_display = (
        'study_plan',
        'id',
        'status',
        'acad_period',
    )


@admin.register(models.ThemesOfTheses)
class ThemesOfThesesAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'uid_1c']
    list_editable = ['uid_1c']
    autocomplete_fields = (
        'supervisors',
        'student',
        'acad_period',
    )
    search_fields = (
        'uid',
        'profile__first_name',
        'profile__last_name',
    )