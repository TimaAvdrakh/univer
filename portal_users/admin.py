from django.contrib import admin
from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    search_fields = [
        'first_name',
        'last_name',
    ]
    list_display = [
        'user',
        'uid',
        'last_name',
        'first_name',
        'middle_name',
    ]


@admin.register(models.ResetPassword)
class ResetPasswordAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'uuid',
        'user',
        'changed',
        'created',
    ]


@admin.register(models.OrganizationToken)
class OrganizationTokenAdmin(admin.ModelAdmin):
    list_display = [
        'organization',
        'token',
        'created',
    ]


@admin.register(models.Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "uid",
    ]


@admin.register(models.MaritalStatus)
class MaritalStatusAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "uid",
    ]


@admin.register(models.Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "uid",
    ]


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [
        "organization",
        # "user",
        "is_student",
        "is_teacher",
        "is_org_admin",
        "is_supervisor",
    ]
