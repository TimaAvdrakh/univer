from django.urls import path
from rest_framework.routers import DefaultRouter
from .viewsets import (
    file_upload,
    ApplicantViewSet,
    QuestionnaireViewSet,
    FamilyMembershipViewSet,
    PrivilegeTypeViewSet,
    DocumentReturnMethodViewSet,
    AddressTypeViewSet,
    RecruitmentPlanViewSet,
    LanguageProficiencyViewSet,
    InternationalCertTypeViewSet,
    GrantTypeViewSet,
    ApplicationStatusViewSet,
    ApplicationViewSet,
    AdmissionCampaignTypeViewSet,
    AdmissionCampaignViewSet
)


app_name = "applicant"
router = DefaultRouter()
router.register(r"applicants", ApplicantViewSet, "applicants")
router.register(r"questionnaires", QuestionnaireViewSet, "questionnaires")
router.register(r"family-memberships", FamilyMembershipViewSet, "family_membership")
router.register(r"privilege-types", PrivilegeTypeViewSet, "privilege-types")
router.register(r"doc-return-methods", DocumentReturnMethodViewSet, "doc_return_methods")
router.register(r"address-types", AddressTypeViewSet, "address_types")
router.register(r"recruitment-plans", RecruitmentPlanViewSet, "recruitment_plans")
router.register(r"lang-levels", LanguageProficiencyViewSet, "lang_levels")
router.register(r"icts", InternationalCertTypeViewSet, "icts")
router.register(r"grant-types", GrantTypeViewSet, "grant_types")
router.register(r"application-statuses", ApplicationStatusViewSet, "application_statuses")
router.register(r"applications", ApplicationViewSet, "applications")
router.register(r"campaign-types", AdmissionCampaignTypeViewSet, "campaign-types")
router.register(r"campaigns", AdmissionCampaignViewSet, "campaigns")
urlpatterns = router.urls

# endpoint для файлов
urlpatterns += [
    path("upload/", file_upload, name='upload'),
]
