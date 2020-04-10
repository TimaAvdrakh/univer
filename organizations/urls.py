from rest_framework.routers import DefaultRouter
from .views import *

app_name = "organizations"
router = DefaultRouter()
router.register(r"prep-levels", PreparationLevelViewSet, "prep_levels")
router.register(r"study-forms", StudyFormViewSet, 'study_forms')
router.register(r"edu-types", EducationTypeViewSet, 'edu_types')
router.register(r"edu-bases", EducationModelViewSet, 'edu_bases')
router.register(r"edu-programs", EducationProgramViewSet, 'edu_programs')
router.register(r"edu-program-groups", EducationProgramGroupViewSet, 'edu_program_groups')
router.register(r"organizations", OrganizationViewSet, 'organizations')
router.register(r"specialities", SpecialityViewSet, 'specialities')
router.register(r"languages", LanguageViewSet, 'languages')
router.register(r"disciplines", DisciplineViewSet, 'disciplines')
urlpatterns = router.urls
