from django.contrib import admin
from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'user',
    )
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
        'status',
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
    list_filter = (
        "is_active",
    )
    list_display = [
        "name",
        "uid",
        "is_active",
    ]


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = (
        'profile__first_name',
        'profile__last_name',
        'profile__middle_name',
    )
    list_display = [
        # "organization",
        "profile",
        "is_student",
        "is_teacher",
        "is_org_admin",
        "is_supervisor",
    ]


@admin.register(models.Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "uid",
    ]


@admin.register(models.AchievementType)
class AchievementTypeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "uid",
    ]


@admin.register(models.Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_filter = (
        'profile',
        'is_active',
        "achievement_type",
        "level",
    )
    list_display = [
        "profile",
        "achievement_type",
        "level",
        "content",
        "is_active",
    ]


@admin.register(models.Position)
class PositionAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        "name",
        "uid",
    ]


@admin.register(models.Teacher)
class PositionAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'profile',
    )
    search_fields = (
        'profile__first_name',
        'profile__last_name',
    )
    list_display = [
        "profile",
        "academic_degree",
        "academic_rank",
        "work_experience_year",
        'work_experience_month',
    ]


@admin.register(models.TeacherPosition)
class PositionAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "profile",
        "position",
        "cathedra",
    )
    list_display = [
        "profile",
        "position",
        "cathedra",
        "is_main",
        "created",
        "study_year",
    ]


@admin.register(models.PhoneType)
class PhoneTypeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "uid",
    ]


@admin.register(models.ProfilePhone)
class ProfilePhoneAdmin(admin.ModelAdmin):
    list_display = [
        "profile",
        "phone_type",
        "value",
        "is_active",
    ]


@admin.register(models.StudentStatus)
class StudentStatusAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "uid",
    ]


@admin.register(models.UsernameRule)
class UsernameRuleAdmin(admin.ModelAdmin):
    list_display = [
        "raw_username",
        "order",
    ]


@admin.register(models.UserCredential)
class UserCredentialAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "user",
    )
    list_display = [
        "user",
        "password",
        "created",
    ]
