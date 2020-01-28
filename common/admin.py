from django.contrib import admin
from . import models
from django.contrib.contenttypes.models import ContentType


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
    autocomplete_fields = (
        'profile',
        'document_type',
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
        'issued_by_str',
    )


@admin.register(models.DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = (
        'name',
        'uid'
    )


@admin.register(models.GovernmentAgency)
class GosOrganizationAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
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


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'model',
    )


@admin.register(models.Log)
class LogAdmin(admin.ModelAdmin):
    search_fields = (
        'object_id',
        'model_name',
    )
    list_display = (
        'model_name',
        'obj_uid',
        'profile',
        'date',
    )


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uid'
    )
