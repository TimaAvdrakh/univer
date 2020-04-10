from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(AdmissionCampaign)
class AdmissionCampaignTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ApplicationStatus)
class ApplicationStatusTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(PrivilegeType)
class PrivilegeTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(DocumentReturnMethod)
class DocumentReturnMethodTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(FamilyMembership)
class FamilyMembershipTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(AddressType)
class AddressTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(AddressClassifier)
class AddressClassifierTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(BudgetLevel)
class BudgetLevelTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(AdmissionCampaignType)
class AdmissionCampaignTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(GrantType)
class GrantTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(InternationalCertType)
class InternationalCertTypeTranslationOptions(TranslationOptions):
    fields = ('name',)
