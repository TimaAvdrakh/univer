from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Max
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import serializers
from rest_framework.validators import ValidationError
from common.models import IdentityDocument, GovernmentAgency, DocumentType
from common.serializers import IdentityDocumentSerializer
from portal_users.serializers import ProfilePhoneSerializer
from portal_users.models import Profile, Role, ProfilePhone
from .models import *
from .token import token_generator


__all__ = [
    'PrivilegeTypeSerializer',
    'PrivilegeSerializer',
    'UserPrivilegeListSerializer',
    'DocumentReturnMethodSerializer',
    'FamilyMemberSerializer',
    'FamilyMembershipSerializer',
    'FamilySerializer',
    'AddressClassifierSerializer',
    'AddressSerializer',
    'AddressTypeSerializer',
    'ApplicantSerializer',
    'ApplicationStatusSerializer',
    'AdmissionApplicationSerializer',
    'AdmissionCampaignSerializer',
    'AdmissionCampaignTypeSerializer',
    'QuestionnaireSerializer',
    'CampaignStageSerializer',
    'DocScanSerializer',

]


class PrivilegeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivilegeType
        fields = "__all__"


class PrivilegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Privilege
        fields = "__all__"


class UserPrivilegeListSerializer(serializers.ModelSerializer):
    privileges = PrivilegeSerializer(many=True, required=True)

    class Meta:
        model = UserPrivilegeList
        fields = "__all__"


class DocumentReturnMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentReturnMethod
        fields = "__all__"


class FamilyMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMembership
        fields = "__all__"


class AddressTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressType
        fields = "__all__"


class AddressClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressClassifier
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = "__all__"


class FamilySerializer(serializers.ModelSerializer):
    members = FamilyMemberSerializer(many=True, required=True)

    class Meta:
        model = Family
        fields = "__all__"


class AdmissionCampaignTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionCampaignType
        fields = "__all__"


class AdmissionCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionCampaign
        fields = "__all__"


# Создает только юзера
class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = "__all__"

    def to_representation(self, instance):
        fields = super().to_representation(instance)
        [fields.pop(field) for field in ['password', 'confirm_password']]
        return fields

    def send_verification_email(self, user: User, to_email: list, password: str):
        subject = 'Verify your email'
        current_site = get_current_site(self.context['request'])
        message = render_to_string('applicant/email/html/verify_email.html', {
            'username': user.username,
            'password': password,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user)
        })
        email = EmailMessage(subject=subject, body=message, to=to_email)
        email.send()
        return

    def validate(self, validated_data):
        # Если не дал согласие на обработку - кинуть ошибку
        if not validated_data["consented"]:
            raise ValidationError({"error": "Consent to process personal data required"})
        # Если идентификационный документ с таким номер уже есть, также кинуть ошибку
        if validated_data["doc_num"]:
            if IdentityDocument.objects.filter(serial_number=validated_data["doc_num"]).exists():
                raise ValidationError({"error": "Identity document with this serial number already exists"})
        else:
            raise ValidationError({"error": "document number is required"})
        # Дальше валидирует сам Django, какие поля указаны в модели
        return validated_data

    def create(self, validated_data):
        if validated_data['password'] != validated_data['confirm_password']:
            raise ValidationError({"error": "passwords don't match"})
        applicant = super().create(validated_data)
        try:
            raw_password = applicant.password
            order_number = Applicant.objects.aggregate(Max("order_number"))["order_number__max"]
            # Самый первый подающий
            if not order_number:
                order_number = 0
            elif order_number == 9999:
                # По ТЗ
                raise ValidationError({"error": "all places are occupied, see ya next year"})
            applicant.order_number = order_number + 1
            applicant.password = make_password(raw_password)
            applicant.confirm_password = make_password(validated_data['confirm_password'])
            username = applicant.generate_login(applicant.order_number)
            # Создаем юзера, который хэндлид авторизацию
            user = User.objects.create(username=username, email=applicant.email)
            # Шифруем пароли
            user.set_password(raw_password=raw_password)
            user.is_active = False
            user.save()
            applicant.user = user
            applicant.save()
            # Создаем профиль т.к. под него завязана авторизация
            profile = Profile.objects.create(user=user)
            Role.objects.create(is_applicant=True, profile=profile)
            # Отправить письмо с верификацией
            try:
                self.send_verification_email(user, [user.email], raw_password)
                # applicant.send_credentials(
                #     uid=user.uid,
                #     username=username,
                #     password=raw_password,
                #     email=applicant.email
                # )
            except Exception as e:
                # Почтовый сервер может не работать
                # applicant.delete()
                print(e)
            # Возвращаем экземпляр абитуриента
            return applicant
        except Exception as e:
            user = applicant.user
            applicant.delete()
            user.delete()
            raise ValidationError({"error": e})


# Создает профиль и роль
class QuestionnaireSerializer(serializers.ModelSerializer):
    family = FamilySerializer(required=True)
    id_doc = IdentityDocumentSerializer(required=True)
    address_of_registration = AddressSerializer(required=False)
    address_of_temp_reg = AddressSerializer(required=False)
    address_of_residence = AddressSerializer(required=True)
    list_of_privileges = UserPrivilegeListSerializer(required=False, many=False)
    phone = ProfilePhoneSerializer(required=True)

    class Meta:
        model = Questionnaire
        fields = "__all__"

    def validate(self, validated_data):
        user = self.context["request"].user
        validated_data["applicant"] = user
        return validated_data

    def create(self, validated_data):
        user = self.context["request"].user
        if user and user.is_authenticated:
            family = validated_data.pop('family')
            id_doc = validated_data.pop('id_doc')
            address_of_registration = validated_data.pop('address_of_registration')
            address_of_temp_reg = validated_data.pop('address_of_temp_reg', None)
            address_of_residence = validated_data.pop('address_of_residence')
            privileges = validated_data.pop('privileges', None)
            phone = validated_data.pop('phone')
            document_type = DocumentType.objects.get(uid=id_doc.pop('document_type'))
            issued_by = GovernmentAgency.objects.get(uid=id_doc.pop('issued_by'))
            id_doc = IdentityDocument.objects.create(
                **id_doc,
                document_type=document_type,
                issued_by=issued_by
            )
            address_of_registration = Address.objects.create(**address_of_registration)
            address_of_residence = Address.objects.create(**address_of_residence)
            members = family.pop('members')
            family = Family.objects.create(**family)
            for member in members:
                member_user = User.objects.create(
                    username=member['email'],
                    password=member['phone']
                )
                member_profile = Profile.objects.create(
                    user=member_user,
                    first_name=member['first_name'],
                    last_name=member['last_name'],
                    middle_name=member['middle_name'],
                    phone=member['phone'],
                    email=member['email']
                )
                member['profile'] = member_profile
                member['family'] = family
                FamilyMember.objects.create(**member)
            validated_data['address_of_registration'] = address_of_registration
            validated_data['address_of_residence'] = address_of_residence
            validated_data['id_doc'] = id_doc
            validated_data['phone'] = ProfilePhone.objects.create(**phone)
            validated_data['family'] = family
            full_questionnaire = super().create(validated_data)
            if address_of_temp_reg:
                full_questionnaire.address_of_temp_reg = Address.objects.create(**address_of_temp_reg)
                if privileges:
                    full_questionnaire.privileges.add(
                        *Privilege.objects.bulk_create(
                            [Privilege(**privilege) for privilege in privileges])
                        )
                    full_questionnaire.save()
                full_questionnaire.save()
            profile = Profile.objects.create(
                user=user,
                first_name=user.applicant.first().first_name,
                last_name=user.applicant.first().last_name,
                middle_name=user.applicant.first().middle_name,
                email=user.applicant.first().email,
            )
            Role.objects.create(profile=profile, is_student=True)
            return full_questionnaire
        else:
            raise ValidationError({"error": f"user undefined"})


# Для этой модели нет REST View, там FileField
# Просто чтобы шло вместе заявкой
class DocScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocScan
        fields = "__all__"


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatus
        fields = "__all__"


class AdmissionApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionApplication
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user
        if user and user.is_authenticated:
            application: AdmissionApplication = super().create(validated_data)
            application.form = user.questionnaires.first()
            application.status = ApplicationStatus.objects.get(code=WAITING_VERIFY)
            application.form.save()
            return application
        else:
            raise ValidationError({"error": "user undefined"})


class CampaignStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignStage
        fields = "__all__"
