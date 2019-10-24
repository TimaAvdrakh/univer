from django.contrib import admin
from . import models


@admin.register(models.AdvisorCheck)
class AdvisorCheckAdmin(admin.ModelAdmin):
    list_display = (
        'study_plan',
        'id',
        'status',
    )
