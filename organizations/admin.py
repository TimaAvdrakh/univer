from django.contrib import admin
from . import models


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
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
    search_fields = (
        'start',
        'end',
    )
    list_filter = (
        'is_study_year',
    )
    list_display = [
        'start',
        'end',
        'uid',
        'is_study_year',
    ]


@admin.register(models.Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        'name',
        'code',
        'uid',
    ]


@admin.register(models.Faculty)
class FacultyAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'dekan',
    )
    list_display = [
        'name',
        'uid',
        'dekan',
    ]


@admin.register(models.Cathedra)
class CathedraAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'headman',
        'kurator',
        'language',
    )
    search_fields = (
        'name',
    )
    list_display = [
        'name',
        'uid',
        'headman',
        'kurator',
        'language',
        'parent',
        'is_subgroup',
    ]


@admin.register(models.EducationProgram)
class EducationProgramAdmin(admin.ModelAdmin):
    list_filter = (
        'group',
    )

    list_display = [
        'name',
        'uid',
        'code',
        'group',
    ]


@admin.register(models.EducationType)
class EducationTypeAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.PreparationLevel)
class PreparationLevelAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
        'shifr',
    ]


@admin.register(models.LoadType)
class LoadTypeAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'load_type2',
    )
    search_fields = (
        'name',
        'load_type2__name',
    )
    list_display = [
        'load_type2',
        'name',
        'uid',
        'created',
        'updated',
    ]


@admin.register(models.LoadType2)
class LoadType2Admin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        'name',
        'uid',
        'number',
        'created',
        'updated',
    ]


@admin.register(models.AcadPeriodType)
class AcadPeriodTypeAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.AcadPeriod)
class AcadPeriodAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
        'number',
    )
    list_display = [
        'name',
        'number',
        'uid',
    ]


@admin.register(models.StudentDiscipline)
class StudentDisciplineAdmin(admin.ModelAdmin):
    search_fields = (
        'uid',
        'student__first_name',
        'student__last_name',
        'student__user__username',
        'uuid1c',
    )
    autocomplete_fields = (
        'student',
        'teacher',
        'author',
        'discipline',
        'study_plan',
        # 'study_year',
        'acad_period',
        'language',
        'study_year',
        'load_type',
    )
    list_filter = [
        'status',
        'study_year',
        # 'sent',
        # 'acad_period',
    ]
    list_display = [
        'student',
        'study_plan',
        'acad_period',
        'discipline',
        'load_type',
        'hours',
        'teacher',
        'language',
        # 'author',
        # 'discipline_code',
        'status',
        'study_year',
        # 'sent',
        'uuid1c',
        'is_active',
    ]


@admin.register(models.Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.TeacherDiscipline)
class TeacherDisciplineAdmin(admin.ModelAdmin):
    search_fields = (
        'uid',
        'teacher__last_name',
        'teacher__first_name',
        'uuid1c',
        'discipline__name',
        'load_type2__name',
        'study_period__start',
        'study_period__end',
    )
    autocomplete_fields = (
        'teacher',
        'discipline',
        'language',
        'study_period',
    )
    # list_filter = [
    #     'teacher',
    #     'discipline',
    #     'load_type2',
    #     'language'
    # ]
    list_display = [
        'teacher',
        'study_period',
        'discipline',
        'load_type2',
        'load_type2_uid_1c',
        'language',
        'uuid1c',
        'is_active',
    ]


@admin.register(models.StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    search_fields = (
        'student__first_name',
        'student__last_name',
        'number',
    )
    autocomplete_fields = (
        'student',
        'advisor',
        'study_period',
    )
    list_display = [
        'student',
        'number',
        'study_period',
        'advisor',
        'speciality',
        'faculty',
        'cathedra',
        'group',
        'education_program',
        'education_type',
        'preparation_level',
        'study_form',
        'education_base',
        'on_base',
        'entry_date',
    ]


# @admin.register(models.Student)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = [
#         'profile',
#         'group',
#     ]


# class StudentModelInline(admin.TabularInline):
#     model = models.Student
#     extra = 0


# @admin.register(models.Group)
# class GroupAdmin(admin.ModelAdmin):
#     inlines = [StudentModelInline]
#     list_display = [
#         'name',
#         'headman',
#         'kurator',
#         'language'
#     ]


@admin.register(models.Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'discipline',
        'required_discipline',
        'speciality',
        'study_period',
    )
    list_display = [
        'study_period',
        'discipline',
        'required_discipline',
        'speciality',
        'created',
        'updated',
    ]


@admin.register(models.Postrequisite)
class PostrequisiteAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'discipline',
        'available_discipline',
        'speciality',
    )
    list_display = [
        'study_period',
        'discipline',
        'available_discipline',
        'speciality',
        'created',
        'updated',
    ]


@admin.register(models.Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )
    list_display = [
        'name',
        'uid',
        'is_language',
    ]


@admin.register(models.StudentDisciplineStatus)
class StatusAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'number',
        'uid',
    ]


@admin.register(models.StudentDisciplineInfo)
class StudentDisciplineInfoAdmin(admin.ModelAdmin):
    search_fields = (
        'uid',
        'student__first_name',
        'student__last_name',
    )
    autocomplete_fields = (
        'acad_period',
        'study_plan',
        'student',
    )
    list_filter = (
        'status',
    )
    list_display = [
        'student',
        'acad_period',
        'study_plan',
        'status',
        'uid',
    ]


@admin.register(models.StudentDisciplineInfoStatus)
class StudentDisciplineInfoStatusAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
        'number'
    ]


@admin.register(models.EducationBase)
class EducationBaseAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
    ]


@admin.register(models.Education)
class EducationAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'institute',
        'profile',
        'document_type',
        'edu_type',
    )
    search_fields = (
        'profile__first_name',
        'profile__last_name',
    )
    list_display = (
        'profile',
        'document_type',
        'edu_type',
        'serial_number',
        'number',
        'given_date',
        'institute',
        'is_active',
    )


@admin.register(models.EducationProgramGroup)
class EducationProgramGroupAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
        'code',
    ]


@admin.register(models.StudyYearCourse)
class StudyYearCourseAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'study_plan',
        'study_year',
    )
    search_fields = (
        'study_plan',
    )
    # list_filter = (
    #     'study_plan',
    # )
    list_display = [
        'study_plan',
        'study_year',
        'course',
    ]


@admin.register(models.DisciplineCycle)
class DisciplineCycleAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'short_name',
        'uid',
    ]


@admin.register(models.DisciplineComponent)
class DisciplineComponentAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'short_name',
        'uid',
    ]


@admin.register(models.ControlForm)
class ControlFormAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'uid',
        'is_exam',
        'is_course_work',
        'is_gos_exam',
        'is_diploma',
        'is_active',
    ]


@admin.register(models.DisciplineCredit)
class DisciplineCreditAdmin(admin.ModelAdmin):
    search_fields = (
        'discipline__name',
    )
    autocomplete_fields = (
        'study_plan',
        'discipline',
        'student',
    )
    list_display = [
        'uuid1c',
        'study_plan',
        'cycle',
        'discipline',
        'credit',
        'is_active',
    ]


@admin.register(models.DisciplineCreditControlForm)
class DisciplineCreditControlFormAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'discipline_credit',
    )
    list_display = [
        'discipline_credit',
        'control_form',
        'is_active',
    ]

admin.site.register(models.EroroText)