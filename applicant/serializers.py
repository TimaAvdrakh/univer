import datetime as dt
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Max
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import get_language
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from common.models import IdentityDocument, GovernmentAgency, DocumentType
from common.serializers import IdentityDocumentSerializer
from portal_users.serializers import ProfilePhoneSerializer
from portal_users.models import Profile, Role, ProfilePhone
from organizations.models import Education
from . import models
from .token import token_generator


class PrivilegeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PrivilegeType
        fields = "__all__"


class PrivilegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Privilege
        fields = "__all__"


class UserPrivilegeListSerializer(serializers.ModelSerializer):
    privileges = PrivilegeSerializer(many=True, required=True)

    class Meta:
        model = models.UserPrivilegeList
        exclude = ['questionnaire']


class DocumentReturnMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentReturnMethod
        fields = "__all__"


class FamilyMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FamilyMembership
        fields = "__all__"


class AddressTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AddressType
        fields = "__all__"


class AddressClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AddressClassifier
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = "__all__"


class FamilyMemberSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=True)

    class Meta:
        model = models.FamilyMember
        fields = "__all__"


class FamilySerializer(serializers.ModelSerializer):
    members = FamilyMemberSerializer(many=True, required=True)

    class Meta:
        model = models.Family
        fields = "__all__"


class AdmissionCampaignTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdmissionCampaignType
        fields = '__all__'


class AdmissionCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdmissionCampaign
        fields = "__all__"


# Создает только юзера
class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Applicant
        fields = "__all__"

    def to_representation(self, instance):
        fields = super().to_representation(instance)
        [fields.pop(field) for field in ['password', 'confirm_password']]
        return fields

    def send_verification_email(self, user: User, to_email: list, password: str):
        subject = 'Verify your email'
        current_site = get_current_site(self.context['request'])
        current_lang = get_language() or 'ru'
        message = render_to_string('applicant/email/html/verify_email.html', {
            'username': user.username,
            'password': password,
            'domain': current_site.domain,
            'lang': current_lang,
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
        campaign_type = self.context['request'].data.get('campaign_type')
        today = dt.date.today()
        campaigns = models.AdmissionCampaign.objects.filter(
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
            order_number = models.Applicant.objects.aggregate(Max("order_number"))["order_number__max"]
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
        model = models.Questionnaire
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
            family = models.Family.objects.create(**family)
            for member in members:
                member_user = User.objects.create(
                    username=member['email'],
                    password=member['phone']
                )
                address = models.Address.objects.create(**member.pop('address'))
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
                models.FamilyMember.objects.create(**member, address=address)
            validated_data['address_of_registration'] = models.Address.objects.create(
                **validated_data.pop('address_of_registration')
            )
            validated_data['address_of_residence'] = models.Address.objects.create(
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
                validated_data['address_of_temp_reg'] = models.Address.objects.create(**address_of_temp_reg)
            if userprivilegelist and len(userprivilegelist['privileges']) > 0:
                privileges = userprivilegelist.pop('privileges')
                user_privilege_list = models.UserPrivilegeList.objects.create(**userprivilegelist)
                for privilege in privileges:
                    models.Privilege.objects.create(**privilege, list=user_privilege_list)
                validated_data['userprivilegelist'] = user_privilege_list
            questionnaire: models.Questionnaire = super().create(validated_data)
            application_set = models.Application.objects.filter(creator=profile)
            if application_set.exists():
                application = application_set.first()
                application.status = models.ApplicationStatus.objects.get(code=models.AWAITS_VERIFICATION)
                application.save()
        except Exception as e:
            questionnaire.delete()
            raise ValidationError({"error": f"an error occurred\n{e}"})
        return questionnaire


class DocScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocScan
        fields = "__all__"


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicationStatus
        fields = "__all__"


class CampaignStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CampaignStage
        fields = "__all__"


class RecruitmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RecruitmentPlan
        fields = "__all__"


class DisciplineMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DisciplineMark
        fields = "__all__"


class TestCertSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TestCert
        fields = "__all__"


class LanguageProficiencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LanguageProficiency
        fields = "__all__"


class InternationalCertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InternationalCertType
        fields = "__all__"


class InternationalCertSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField(read_only=True, required=False)

    def get_info(self, cert: models.InternationalCert):
        info = {
            'type': cert.type.name,
            'language_proficiency': cert.language_proficiency.code,

        }
        return info

    class Meta:
        model = models.InternationalCert
        fields = "__all__"


class GrantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GrantType
        fields = "__all__"


class GrantSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField(read_only=True, required=False)

    def get_info(self, grant: models.Grant):
        info = {
            'type': grant.type.name,
            'speciality': grant.speciality.name,
            'scan': {
                'name': grant.scan.name,
                'path': grant.scan.path,
            }
        }
        return info

    class Meta:
        model = models.Grant
        fields = "__all__"


class DirectionChoiceSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField(required=False, read_only=True)

    def get_info(self, direction: models.DirectionChoice):
        info = {
            'prep_level': direction.prep_level.name,
            'study_form': direction.study_form.name,
            'education_program': direction.education_program.name,
            'education_program_group': direction.education_program_group.name,
            'education_base': direction.education_base.name,
            'education_language': direction.education_language.name
        }
        return info

    class Meta:
        model = models.DirectionChoice
        fields = "__all__"


class TestResultSerializer(serializers.ModelSerializer):
    disciplines = DisciplineMarkSerializer(required=True, many=True)
    test_certificate = TestCertSerializer(required=True)
    info = serializers.SerializerMethodField(read_only=True, required=False)

    def get_info(self, result: models.TestResult):
        info = {
            'disciplines': [{
                'discipline': d.discipline.name,
                'mark': d.mark
            } for d in result.disciplines.all()],
            'test_certificate': {
                'language': result.test_certificate.language.name,
                'scan': {
                    'name': result.test_certificate.scan.name,
                    'path': result.test_certificate.scan.path,
                }
            }
        }
        return info

    class Meta:
        model = models.TestResult
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField(required=False, read_only=True)

    def get_info(self, edu: models.Education):
        info = {
            'doc_type': edu.document_type.name,
            'edu_type': edu.edu_type.name,
            'institute': edu.institute_text or edu.institute.name,
            'study_form': edu.study_form.name,
            'speciality': edu.speciality.name,
            'scan': {
                'name': edu.scan.name,
                'path': edu.scan.path,
            }
        }
        return info

    class Meta:
        model = models.Education
        exclude = ['profile']


class ApplicationLiteSerializer(serializers.ModelSerializer):
    status_info = serializers.ReadOnlyField()
    applicant = serializers.ReadOnlyField()

    class Meta:
        model = models.Application
        fields = ['uid', 'status_info', 'applicant', 'created', 'updated']

    def create(self, validated_data: dict):
        application = None
        creator: Profile = self.context['request'].user.profile
        try:
            # Ориентируемся на приемную кампанию
            my_campaign = creator.user.applicant.campaign
            # Проверяем если абитуриент выбрал больше направлений, чем задано в приемной кампании
            directions = validated_data.pop('directions')
            if my_campaign.chosen_directions_max_count < len(directions):
                raise ValidationError({"error": "chosen directions maximum count exceeded"})
            # Если есть заполненная анкета, статус будет "Ожидает проверки", иначе - "Без анкеты"
            has_questionnaire: bool = models.Questionnaire.objects.filter(creator=creator).exists()
            if has_questionnaire:
                status = models.AWAITS_VERIFICATION
            else:
                status = models.NO_QUESTIONNAIRE
            status = models.ApplicationStatus.objects.get(code=status)
            # На основании забитых данных абитуриентом создаем его заявление
            # Предыдущее образование
            previous_education = Education.objects.create(
                profile=creator,
                **validated_data.pop('previous_education')
            )
            # Результаты теста ЕНТ/КТА
            test_result = validated_data.pop('test_result')
            test_certificate = models.TestCert.objects.create(
                profile=creator,
                **test_result.pop('test_certificate')
            )
            disciplines = models.DisciplineMark.objects.bulk_create([
                models.DisciplineMark(profile=creator, **discipline) for discipline in test_result.pop('disciplines')
            ])
            test_result = models.TestResult.objects.create(profile=creator, test_certificate=test_certificate)
            test_result.disciplines.add(*disciplines)
            test_result.save()
            # Международный сертификат, только если в кампании указано, что он принимаются сертифиакаты
            if my_campaign.inter_cert_foreign_lang:
                international_cert = models.InternationalCert(profile=creator,
                                                              **validated_data.pop('international_cert'))
            else:
                international_cert = None
            # Грант
            grant = validated_data.pop('grant', None)
            if grant:
                grant = models.Grant.objects.create(profile=creator, **grant)
            else:
                grant = None
            # Выбор направлений.
            # TODO сверять направления и основания для поступления с грантом.
            #  Если грант дан только на Специальность #1, а в каком-то направлении
            #  стоит Специальность #X и основа поступления "Бюджет" кинуть ошибку -> удалить заявление
            directions = models.DirectionChoice.objects.bulk_create([
                models.DirectionChoice(profile=creator, **direction) for direction in directions
            ])
            application = models.Application.objects.create(
                status=status,
                previous_education=previous_education,
                test_result=test_result,
                international_cert=international_cert,
                grant=grant,
                creator=creator,
                questionnaire=models.Questionnaire.objects.filter(creator=creator).first()
            )
            application.directions.add(*directions)
            application.save()
        except Exception as e:
            if application and isinstance(application, models.Application):
                application.delete()
            raise ValidationError({"error": f"an error occurred\n{e}"})
        return application

    def update(self, instance, validated_data: dict):
        user = self.context['request'].user.profile
        if user == instance.creator or user.role.is_mod:
            validated_data['status'] = models.ApplicationStatus.objects.get(code=models.AWAITS_VERIFICATION)
            application = super().update(instance, validated_data)
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
        model = models.Application
        fields = '__all__'
