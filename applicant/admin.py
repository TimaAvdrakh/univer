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
    TestResult,
    Application,
    AdmissionDocument,
    Document1C,
]

admin.site.register(models)
