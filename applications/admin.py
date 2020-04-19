from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.Type)
class TypeAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        'uid',
        'name',
    ]


@admin.register(models.SubType)
class TypeAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        'uid',
        'name',
        'type',
        'example',
    ]


admin.site.register(models.Example)
admin.site.register(models.Status)