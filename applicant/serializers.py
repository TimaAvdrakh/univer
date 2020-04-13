from django.core.mail import EmailMessage
import datetime as dt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Max
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework.exceptions import ValidationError
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

from organizations.models import Education
from .models import (
    PrivilegeType,
    Privilege,
    UserPrivilegeList,
    DocumentReturnMethod,
    FamilyMembership,
    AddressType,
    AddressClassifier,
    Address,
    FamilyMember,
    Family,
    AdmissionCampaign,
    Applicant,
    Questionnaire,
    Application,
    DocScan,
    ApplicationStatus,
    CampaignStage,
    RecruitmentPlan,
    DisciplineMark,
    TestCert,
    LanguageProficiency,
    InternationalCertType,
    InternationalCert,
    GrantType,
    Grant,
    DirectionChoice,
    TestResult,
    AdmissionCampaignType,
    AWAITS_VERIFICATION,
    NO_QUESTIONNAIRE
)
from .token import token_generator


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
        exclude = ['questionnaire']


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
    address = AddressSerializer(required=True)

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
        fields = '__all__'


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
        campaign_type: AdmissionCampaignType = self.context['request'].data.get('campaign_type')
        today = dt.date.today()
        campaigns = AdmissionCampaign.objects.filter(
            type=campaign_type,
            is_active=True,
            year=dt.datetime.now().year,
            start_date__lte=today,
            end_date__gte=today
        )
        if campaigns.exists():
            validated_data['campaign'] = campaigns.first()
        else:
            raise ValidationError({'error': 'no campaign found'})
        return validated_data

    def create(self, validated_data):
        if validated_data['password'] != validated_data['confirm_password']:
            raise ValidationError({"error": "passwords don't match"})
        # TODO проверку на то, что есть приемные кампании, которые принимают полученный уровень образования
        #  если он, есть продолжить регистрацию и создать абитуриента с профилем. Если нет вернуть ошибку и сообшение
        #  о том, что нет приемных кампаний с таким уровнем подготовки
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
            profile = Profile.objects.create(
                user=user,
                first_name=applicant.first_name,
                last_name=applicant.last_name,
                middle_name=applicant.middle_name,
                email=applicant.email
            )
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
    userprivilegelist = UserPrivilegeListSerializer(required=False, many=False)
    phone = ProfilePhoneSerializer(required=True)

    class Meta:
        model = Questionnaire
        fields = "__all__"

    def create(self, validated_data):
        questionnaire = None
        try:
            profile = self.context["request"].user.profile
            validated_data["creator"] = profile
            family = validated_data.pop('family')
            address_of_temp_reg = validated_data.pop('address_of_temp_reg', None)
            userprivilegelist = validated_data.pop('userprivilegelist', None)
            members = family.pop('members')
            family = Family.objects.create(**family)
            for member in members:
                member_user = User.objects.create(
                    username=member['email'],
                    password=member['phone']
                )
                address = Address.objects.create(**member.pop('address'))
                member_profile = Profile.objects.create(
                    user=member_user,
                    first_name=member['first_name'],
                    last_name=member['last_name'],
                    middle_name=member['middle_name'],
                    phone=member['phone'],
                    email=member['email'],
                )
                member['profile'] = member_profile
                member['family'] = family
                FamilyMember.objects.create(**member, address=address)
            validated_data['address_of_registration'] = Address.objects.create(
                **validated_data.pop('address_of_registration')
            )
            validated_data['address_of_residence'] = Address.objects.create(
                **validated_data.pop('address_of_residence')
            )
            id_doc = validated_data.pop('id_doc')
            validated_data['id_doc'] = IdentityDocument.objects.create(
                **id_doc,
                document_type=DocumentType.objects.get(uid=id_doc.pop('document_type')),
                issued_by=GovernmentAgency.objects.get(uid=id_doc.pop('issued_by'))
            )
            validated_data['phone'] = ProfilePhone.objects.create(**validated_data.pop('phone'))
            validated_data['family'] = family
            if address_of_temp_reg:
                validated_data['address_of_temp_reg'] = Address.objects.create(**address_of_temp_reg)
            if userprivilegelist and len(userprivilegelist['privileges']) > 0:
                privileges = userprivilegelist.pop('privileges')
                user_privilege_list = UserPrivilegeList.objects.create(**userprivilegelist)
                for privilege in privileges:
                    Privilege.objects.create(**privilege, list=user_privilege_list)
                validated_data['userprivilegelist'] = user_privilege_list
            questionnaire: Questionnaire = super().create(validated_data)
            application_set = Application.objects.filter(creator=profile)
            if application_set.exists:
                application = application_set.first()
                application.status = ApplicationStatus.objects.get(code=AWAITS_VERIFICATION)
                application.save()
        except Exception as e:
            questionnaire.delete()
            raise ValidationError({"error": f"an error occurred\n{e}"})
        return questionnaire


class DocScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocScan
        fields = "__all__"


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatus
        fields = "__all__"


class CampaignStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignStage
        fields = "__all__"


class RecruitmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentPlan
        fields = "__all__"


class DisciplineMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplineMark
        fields = "__all__"


class TestCertSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCert
        fields = "__all__"


class LanguageProficiencySerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageProficiency
        fields = "__all__"


class InternationalCertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternationalCertType
        fields = "__all__"


class InternationalCertSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternationalCert
        fields = "__all__"


class GrantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrantType
        fields = "__all__"


class GrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grant
        fields = "__all__"


class DirectionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectionChoice
        fields = "__all__"


class TestResultSerializer(serializers.ModelSerializer):
    disciplines = DisciplineMarkSerializer(required=True, many=True)
    test_certificate = TestCertSerializer(required=True)

    class Meta:
        model = TestResult
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ['profile']


class ApplicationLiteSerializer(serializers.ModelSerializer):
    status_info = serializers.ReadOnlyField()
    applicant = serializers.ReadOnlyField()

    class Meta:
        model = Application
        fields = ['uid', 'status_info', 'applicant', 'created', 'updated']

    def create(self, validated_data: dict):
        application = None
        creator: Profile = self.context['request'].user.profile
        try:
            # Ориентируемся на приемную кампанию
            my_campaign: AdmissionCampaign = creator.user.applicant.campaign
            # Проверяем если абитуриент выбрал больше направлений, чем задано в приемной кампании
            directions: dict = validated_data.pop('directions')
            if my_campaign.chosen_directions_max_count < len(directions):
                raise ValidationError({"error": "chosen directions maximum count exceeded"})
            # Если есть заполненная анкета, статус будет "Ожидает проверки", иначе - "Без анкеты"
            has_questionnaire: bool = Questionnaire.objects.filter(creator=creator).exists()
            if has_questionnaire:
                status = AWAITS_VERIFICATION
            else:
                status = NO_QUESTIONNAIRE
            status: ApplicationStatus = ApplicationStatus.objects.get(code=status)
            # На основании забитых данных абитуриентом создаем его заявление
            # Предыдущее образование
            previous_education: Education = Education.objects.create(profile=creator,
                                                                     **validated_data.pop('previous_education'))
            # Результаты теста ЕНТ/КТА
            test_result: dict = validated_data.pop('test_result')
            test_certificate: TestCert = TestCert.objects.create(profile=creator,
                                                                 **test_result.pop('test_certificate'))
            disciplines: [DisciplineMark] = DisciplineMark.objects.bulk_create([
                DisciplineMark(profile=creator, **discipline) for discipline in test_result.pop('disciplines')
            ])
            test_result: TestResult = TestResult.objects.create(profile=creator, test_certificate=test_certificate)
            test_result.disciplines.add(*disciplines)
            test_result.save()
            # Международный сертификат, только если в кампании указано, что он принимаются сертифиакаты
            if my_campaign.inter_cert_foreign_lang:
                international_cert = InternationalCert(profile=creator, **validated_data.pop('international_cert'))
            else:
                international_cert = None
            # Грант
            grant: dict = validated_data.pop('grant', None)
            if grant:
                grant: Grant = Grant.objects.create(profile=creator, **grant)
            else:
                grant: None = None
            # Выбор направлений.
            # TODO сверять направления и основания для поступления с грантом.
            #  Если грант дан только на Специальность #1, а в каком-то направлении
            #  стоит Специальность #X и основа поступления "Бюджет" кинуть ошибку -> удалить заявление
            directions: [DirectionChoice] = DirectionChoice.objects.bulk_create([
                DirectionChoice(profile=creator, **direction) for direction in directions
            ])
            application: Application = Application.objects.create(
                status=status,
                previous_education=previous_education,
                test_result=test_result,
                international_cert=international_cert,
                grant=grant,
                creator=creator,
                questionnaire=Questionnaire.objects.filter(creator=creator).first()
            )
            application.directions.add(*directions)
            application.save()
        except Exception as e:
            if application and isinstance(application, Application):
                application.delete()
            raise ValidationError({"error": f"an error occurred\n{e}"})
        return application

    def update(self, instance: Application, validated_data: dict):
        user = self.context['request'].user.profile
        if user == instance.creator or user.role.is_mod:
            validated_data['status'] = ApplicationStatus.objects.get(code=AWAITS_VERIFICATION)
            application: Application = super().update(instance, validated_data)
            return application
        else:
            raise ValidationError({"error": "you don't have rights to edit application"})


class ApplicationSerializer(ApplicationLiteSerializer):
    previous_education = EducationSerializer(required=True)
    test_result = TestResultSerializer(required=True)
    international_cert = InternationalCertSerializer(required=False)
    grant = GrantSerializer(required=False)
    directions = DirectionChoiceSerializer(required=True, many=True)

    class Meta:
        model = Application
        fields = '__all__'
