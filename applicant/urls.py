from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .viewsets import *


app_name = "applicant"
router = DefaultRouter()
router.register(r"applicants", ApplicantViewSet, "applicants")
router.register(r"questionnaires", QuestionnaireViewSet, "questionnaires")
router.register(r"applications", AdmissionApplicationViewSet, "admission-applications")
urlpatterns = router.urls

# endpoint для файлов
urlpatterns += [
    path("upload/", file_upload, name='upload'),
    path("login/", ApplicantLogin.as_view(), name='login'),
]
