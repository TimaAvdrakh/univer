from django.contrib import admin
from .models import *

models = [
    AdmissionCampaignType,
    AdmissionCampaign,
    Applicant,
    DocScan,
    ApplicationStatus,
    Questionnaire,
    AdmissionApplication,
    CampaignStage,
]

# Пока так зарегаю, если нужно - расширим админку для модели
admin.site.register(models)
