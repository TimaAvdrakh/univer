from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.Organization)
class OrganizationTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.StudyForm)
class StudyFormTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Speciality)
class SpecialityTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Faculty)
class FacultyTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Cathedra)
class CathedraTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.EducationProgram)
class EducationProgramTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.EducationType)
class EducationTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.PreparationLevel)
class PreparationLevelTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Discipline)
class DisciplineTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(models.LoadType)
class LoadTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.AcadPeriodType)
class AcadPeriodTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.AcadPeriod)
class AcadPeriodTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Language)
class LanguageTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.LoadType2)
class LoadType2TranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.Group)
class GroupTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.StudentDisciplineStatus)
class StatusTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.StudentDisciplineInfoStatus)
class StudentDisciplineInfoStatusTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.EducationBase)
class EducationBaseTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.EducationProgramGroup)
class EducationProgramGroupTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.DisciplineCycle)
class DisciplineCycleTranslationOptions(TranslationOptions):
    fields = ('name', 'short_name',)


@register(models.DisciplineComponent)
class DisciplineComponentTranslationOptions(TranslationOptions):
    fields = ('name', 'short_name',)


@register(models.ControlForm)
class ControlFormTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(models.DisciplineGroup)
class DisciplineGroupTranslationOptions(TranslationOptions):
    fields = ('name',)

