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
admin.site.register(models.IdentityDoc)
admin.site.register(models.ServiceDoc)
admin.site.register(models.Status)

@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'profile',
    )
    list_display = [
        'type',
        'status',
        'comment',
        'responsible',
        'identity_doc',
    ]
admin.site.register(models.SubApplication)