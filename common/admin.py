from django.contrib import admin
from . import models


@admin.register(models.CourseAcadPeriodPermission)
class CourseAcadPeriodPermissionAdmin(admin.ModelAdmin):
    list_display = [
        'registration_period',
        'uid',
        'course',
        'acad_period',
    ]


class CourseAcadPeriodPermissionInline(admin.TabularInline):
    extra = 1
    model = models.CourseAcadPeriodPermission


@admin.register(models.RegistrationPeriod)
class RegistrationForDisciplineAdmin(admin.ModelAdmin):
    inlines = [
        CourseAcadPeriodPermissionInline,
    ]
    list_display = [
        'name',
        'uid',
        'start_date',
        'end_date',
    ]

