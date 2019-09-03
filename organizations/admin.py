from django.contrib import admin
from . import models


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]


@admin.register(models.StudyForm)
class StudyFormAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.StudyPeriod)
class StudyPeriodAdmin(admin.ModelAdmin):
    list_display = [
        'start',
        'end',
        'uid',
    ]


@admin.register(models.Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'uid',
    ]


@admin.register(models.Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.Cathedra)
class CathedraAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.EducationProgram)
class EducationProgramAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.EducationType)
class EducationTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.PreparationLevel)
class PreparationLevelAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.LoadType)
class LoadTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.AcadPeriodType)
class AcadPeriodTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.AcadPeriod)
class AcadPeriodAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.StudentDiscipline)
class StudentDisciplineAdmin(admin.ModelAdmin):
    list_display = [
        'study_plan',
        'acad_period',
        'discipline',
        'load_type',
        'hours',
        'teacher',
    ]


@admin.register(models.Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.TeacherDiscipline)
class TeacherDisciplineAdmin(admin.ModelAdmin):
    list_display = [
        'teacher',
        'discipline',
        'load_type',
        'language'
    ]
