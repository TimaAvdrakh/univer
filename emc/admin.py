from django.contrib import admin
from .models import EMC


@admin.register(EMC)
class EMCAdmin(admin.ModelAdmin):
    search_fields = (
        'discipline',
    )
    list_display = [
        'discipline',
        'author',
        'description',
        'language'
    ]
