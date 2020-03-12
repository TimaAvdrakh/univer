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
class InterestAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'supervisors',
        'student',
        'acad_period',
        'study_plan'
    )
    search_fields = (
        'uid',
        'profile__first_name',
        'profile__last_name',
    )