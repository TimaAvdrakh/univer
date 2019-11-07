from django.contrib import admin
from . import models


@admin.register(models.CourseAcadPeriodPermission)
class CourseAcadPeriodPermissionAdmin(admin.ModelAdmin):
    list_filter = (
        'registration_period',
        'course',
    )
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


@admin.register(models.IdentityDocument)
class IdentityDocumentAdmin(admin.ModelAdmin):
    list_filter = (
        'profile',
        'document_type',
        'serial_number',
        'number',
        'validity_date',
        'issued_by',
    )
    list_display = (
        'profile',
        'document_type',
        'serial_number',
        'number',
        'given_date',
        'validity_date',
        'issued_by',
    )


@admin.register(models.DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uid'
    )


@admin.register(models.GovernmentAgency)
class GosOrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uid'
    )


@admin.register(models.Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uid'
    )


@admin.register(models.Citizenship)
class CitizenshipAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uid'
    )


@admin.register(models.CreditCoeff)
class CreditCoeffAdmin(admin.ModelAdmin):
    list_display = (
        'start_year',
        'coeff'
    )
