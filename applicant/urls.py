from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from . import viewsets


app_name = "applicant"
router = DefaultRouter()
router.register(r"applicants", viewsets.ApplicantViewSet, "applicants")
router.register(r"questionnaires", viewsets.QuestionnaireViewSet, "questionnaires")
router.register(r"family-memberships", viewsets.FamilyMembershipViewSet, "family_membership")
router.register(r"privilege-types", viewsets.PrivilegeTypeViewSet, "privilege-types")
router.register(r"doc-return-methods", viewsets.DocumentReturnMethodViewSet, "doc_return_methods")
router.register(r"address-types", viewsets.AddressTypeViewSet, "address_types")
router.register(r"recruitment-plans", viewsets.RecruitmentPlanViewSet, "recruitment_plans")
router.register(r"lang-levels", viewsets.LanguageProficiencyViewSet, "lang_levels")
router.register(r"icts", viewsets.InternationalCertTypeViewSet, "icts")
router.register(r"grant-types", viewsets.GrantTypeViewSet, "grant_types")
router.register(r"application-statuses", viewsets.ApplicationStatusViewSet, "application_statuses")
router.register(r"applications", viewsets.ApplicationViewSet, "applications")
router.register(r"campaign-types", viewsets.AdmissionCampaignTypeViewSet, "campaign-types")
router.register(r"campaigns", viewsets.AdmissionCampaignViewSet, "campaigns")
router.register(r"addresses", viewsets.AddressViewSet, "addresses")
urlpatterns = router.urls

# endpoint для файлов
urlpatterns += [
    path("upload/", viewsets.file_upload, name='upload'),
    re_path(
        "activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/",
        viewsets.activate,
        name='activate'
    )
]
