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


@admin.register(models.CredentialsEmailTask)
class CredentialsEmailTaskAdmin(admin.ModelAdmin):
    list_display = [
        'to',
        'username',
        'password',
        'is_success',
    ]


@admin.register(models.NotifyAdvisorTask)
class NotifyAdvisorTaskAdmin(admin.ModelAdmin):
    list_filter = (
        'is_success',
    )
    list_display = [
        'stud_discipline_info',
        'is_success',
    ]


@admin.register(models.AdvisorRejectedBidTask)
class AdvisorRejectedBidTaskTaskAdmin(admin.ModelAdmin):
    list_filter = (
        'is_success',
    )
    list_display = [
        'study_plan',
        'is_success',
    ]


@admin.register(models.PlanCloseJournalTask)
class PlanCloseJournalTaskAdmin(admin.ModelAdmin):
    list_display = [
        'date_time',
        'is_success',
    ]
