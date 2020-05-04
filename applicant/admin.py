from django.contrib import admin
from .models import *

models = [
    PrivilegeType,
    DocumentReturnMethod,
    FamilyMembership,
    BudgetLevel,
    InternationalCertType,
    GrantType,
    AddressClassifier,
    Address,
    Family,
    FamilyMember,
    AdmissionCampaignType,
    AdmissionCampaign,
    Applicant,
    DocScan,
    ApplicationStatus,
    Questionnaire,
    UserPrivilegeList,
    Privilege,
    CampaignStage,
    RecruitmentPlan,
    DisciplineMark,
    TestCert,
    LanguageProficiency,
    InternationalCert,
    Grant,
    DirectionChoice,
    TestResult,
    Application,
    AdmissionDocument,
]

admin.site.register(models)
