from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .viewsets import (
    ApplicantViewSet,
    QuestionnaireViewSet,
    AdmissionApplicationViewSet,
    FamilyMembershipViewSet,
    PrivilegeTypeViewSet,
    DocumentReturnMethodViewSet,
    file_upload
)


app_name = "applicant"
router = DefaultRouter()
router.register(r"applicants", ApplicantViewSet, "applicants")
router.register(r"questionnaires", QuestionnaireViewSet, "questionnaires")
router.register(r"applications", AdmissionApplicationViewSet, "admission-applications")
router.register(r"family-memberships", FamilyMembershipViewSet, "family-membership")
router.register(r"privilege-types", PrivilegeTypeViewSet, "privilege-types")
router.register(r"doc-return-methods", DocumentReturnMethodViewSet, "doc-return-methods")
urlpatterns = router.urls

# endpoint для файлов
urlpatterns += [
    path("upload/", file_upload, name='upload'),
]
