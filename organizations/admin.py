from django.contrib import admin
from . import models


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]


@admin.register(models.StudyForm)
class StudyFormAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]
