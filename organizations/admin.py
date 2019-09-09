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


@admin.register(models.LoadType)
class LoadTypeAdmin(admin.ModelAdmin):
    list_display = [
        'load_type2',
        'name',
        'uid',
    ]


@admin.register(models.LoadType2)
class LoadType2Admin(admin.ModelAdmin):
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
        'student',
        'study_plan',
        'acad_period',
        'discipline',
        'load_type',
        'hours',
        'teacher',
        'author',
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
        'load_type2',
        'language'
    ]


@admin.register(models.StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'study_period',
        'speciality',
        'faculty',
        'cathedra',
        'education_program',
        'education_type',
        'preparation_level',
        'study_form',
        'on_base',
    ]


@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'profile',
        'group',
    ]


class StudentModelInline(admin.TabularInline):
    model = models.Student
    extra = 0


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = [StudentModelInline]
    list_display = [
        'name',
        'headman',
        'kurator',
        'supervisor',
        'language'
    ]


@admin.register(models.Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_filter = [
        'discipline',
        'required_discipline',
    ]
    list_display = [
        'study_period',
        'discipline',
        'required_discipline',
        'speciality',
    ]


@admin.register(models.Postrequisite)
class PostrequisiteAdmin(admin.ModelAdmin):
    list_filter = [
        'discipline',
        'available_discipline',
    ]
    list_display = [
        'study_period',
        'discipline',
        'available_discipline',
        'speciality',
    ]


@admin.register(models.Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
        'is_language',
    ]


@admin.register(models.StudentDisciplineStatus)
class StatusAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]
