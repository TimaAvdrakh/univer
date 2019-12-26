from django.contrib import admin
from . import models


@admin.register(models.DocumentChangeLog)
class DocumentChangeLogAdmin(admin.ModelAdmin):
    list_display = (
        'document',
        'content_type',
        'object_id',
        'status',
        'errors',
    )
