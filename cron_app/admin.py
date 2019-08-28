from django.contrib import admin
from . import models


@admin.register(models.EmailTask)
class EmailTaskAdmin(admin.ModelAdmin):
    list_display = [
        'to',
        'subject',
        'message',
        'is_success'
    ]


@admin.register(models.ResetPasswordUrlSendTask)
class ResetPasswordUrlSendTaskAdmin(admin.ModelAdmin):
    list_display = [
        'reset_password',
        'is_success'
    ]
