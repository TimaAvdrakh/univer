import datetime as dt
from django.core.mail import EmailMessage, send_mail
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
    info = serializers.SerializerMethodField()

    def get_info(self, address: models.Address):
        info = {
            'country': {
                'uid': address.country.uid,
                'name': address.country.name
            }
        }
        if address.country.code == 'KZ':
            if address.region:
                info.update({
                    'region': {
                        'uid': address.region.uid,
                        'name': address.region.name,
                    }
                })
            if address.district:
                info.update({
                    'district': {
                        'uid': address.district.uid,
                        'name': address.district.name,
                    }
                })
            if address.city:
                info.update({
                    'city': {
                        'uid': address.city.uid,
                        'name': address.city.name,
                    }
                })
            if address.locality:
                info.update({
                    'locality': {
                        'uid': address.locality.uid,
                        'name': address.locality.name,
                    }
                })
        return info

    class Meta:
        model = models.Address
        fields = "__all__"


class FamilyMemberSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=True)
    address_matches = serializers.CharField(required=False, allow_null=True)

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


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Applicant
        fields = "__all__"

    def to_representation(self, instance):
        fields = super().to_representation(instance)
        [fields.pop(field) for field in ['password', 'confirm_password']]
        return fields

    def send_verification_email(self, user: User, to_email: list, password: str):
        subject = 'Подтвердите регистрацию'
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
        # Если идентификационный документ с таким номер уже есть, также кинуть ошибку
        if validated_data["doc_num"]:
            if IdentityDocument.objects.filter(serial_number=validated_data["doc_num"]).exists():
                raise ValidationError({"error": "id_exists"})
        # Дальше валидирует сам Django, какие поля указаны в модели
        campaign_type = self.context['request'].data.get('campaign_type')
        today = dt.date.today()
        campaigns = models.AdmissionCampaign.objects.filter(
            type=campaign_type,
            is_active=True,
            year=today.year,
            start_date__lte=today,
            end_date__gte=today
        )
        if campaigns.exists():
            validated_data['campaign'] = campaigns.first()
        else:
            raise ValidationError({"error": "no_campaign"})
        return validated_data

    def create(self, validated_data):
        if validated_data['password'] != validated_data['confirm_password']:
            raise ValidationError({"error": "pass_no_match"})
        applicant = super().create(validated_data)
        try:
            raw_password = applicant.password
            order_number = models.Applicant.objects.aggregate(Max("order_number"))["order_number__max"]
            # Самый первый подающий
            if not order_number:
                order_number = 0
            elif order_number == 9999:
                # По ТЗ
                raise ValidationError({"error": "places_exceeded"})
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


class IdentityDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IdentityDocument
        exclude = ['profile']


class QuestionnaireSerializer(serializers.ModelSerializer):
    family = FamilySerializer(required=True)
    id_doc = IdentityDocumentSerializer(required=True)
    address_of_registration = AddressSerializer(required=False)
    address_of_temp_reg = AddressSerializer(required=False, allow_null=True)
    address_of_residence = AddressSerializer(required=True)
    userprivilegelist = UserPrivilegeListSerializer(required=False, many=False)
    phone = ProfilePhoneSerializer(required=True)
    info = serializers.SerializerMethodField()

    class Meta:
        model = models.Questionnaire
        fields = "__all__"

    def get_info(self, q: models.Questionnaire):

        info = {
            'nationality': {
                'uid': q.nationality.uid,
                'name': q.nationality.name,
            }
        }
        return info

    def validate(self, validated_data: dict):
        address_of_registration = validated_data.get('address_of_registration')
        address_of_temp_reg = validated_data.get('address_of_temp_reg', None)
        address_of_residence = validated_data.get('address_of_residence')

        family: dict = validated_data.get('family')
        members: dict = family.pop('members')
        # Если хоть у одного члена семьи будет стоять временный адрес регистрации,
        # а абитуриент не указал его - кидать ошибку
        if any(filter(lambda x: x['address_matches'] == 'm_temp', members)) and not address_of_temp_reg:
            raise ValidationError({
                "error": "no_temp_reg_for_member",
                "message": "Temporary address wasn't provided and set as address of member"
            })
        member: dict
        for member in members:
            address = member.pop('address')
            address_match = member.pop('address_matches')
            if address_match == 'm_reg':
                address = address_of_registration
            elif address_match == 'm_temp':
                address = address_of_temp_reg
            elif address_match == 'm_res':
                address = address_of_residence
            elif address_match == 'no_match':
                address['name_en'] = address['name_kk'] = address['name_ru']
            member['address'] = address
        family['members'] = members

        return validated_data

    def create(self, validated_data):
        profile = self.context["request"].user.profile
        questionnaire = None
        try:
            validated_data["creator"] = profile
            family = models.Family.objects.filter(profile=profile)
            if family.exists():
                family = family.first()
            else:
                family = validated_data.pop('family')
                members = family.pop('members')
                family = models.Family.objects.create(**family, profile=profile)
                for member in members:
                    user = User.objects.create(
                        username=member['email'],
                        password=member['phone']
                    )
                    profile = Profile.objects.create(
                        user=user,
                        first_name=member['first_name'],
                        last_name=member['last_name'],
                        middle_name=member['middle_name'],
                        phone=member['phone'],
                        email=member['email'],
                    )
                    address = models.Address.objects.create(**member.pop('address'))
                    member.update({
                        'profile': profile,
                        'family': family,
                        'address': address
                    })
                    models.FamilyMember.objects.create(**member)

            address_of_registration = validated_data.pop('address_of_registration')
            address_of_registration.pop('type', None)
            models.Address.objects.create(
                type=models.AddressType.get_type(models.AddressType.REGISTRATION),
                **address_of_registration)

            address_of_residence = validated_data.pop('address_of_residence')
            models.Address.objects.create(
                type=models.AddressType.get_type(models.AddressType.RESIDENCE),
                **address_of_residence)
            address_of_temp_reg = validated_data.pop('address_of_temp_reg', None)
            if address_of_temp_reg:
                models.Address.objects.create(
                    type=models.AddressType.get_type(models.AddressType.TEMP_REG),
                    **address_of_temp_reg)

            id_doc = IdentityDocument.objects.filter(profile=profile)
            if id_doc.exists():
                id_doc = id_doc.first()
            else:
                id_doc = IdentityDocument.objects.create(
                    profile=profile,
                    **validated_data.pop('id_doc'),
                )
            phone = ProfilePhone.objects.filter(profile=profile)
            if phone.exists():
                phone = phone.first()
            else:
                phone = ProfilePhone.objects.create(
                    **validated_data.pop('phone'),
                    profile=profile
                )
            validated_data.update({
                'address_of_registration': address_of_registration,
                'address_of_residence': address_of_residence,
                'id_doc': id_doc,
                'phone': phone,
                'family': family,
            })
            user_privilege_list = validated_data.pop('userprivilegelist', None)
            if user_privilege_list:
                privileges = user_privilege_list.pop('privileges')
                user_privilege_list = models.UserPrivilegeList.objects.create(
                    **user_privilege_list,
                    profile=profile
                )
                for privilege in privileges:
                    models.Privilege.objects.create(
                        **privilege,
                        list=user_privilege_list,
                        profile=profile
                    )
                validated_data['userprivilegelist'] = user_privilege_list
            questionnaire = super().create(validated_data)
            applications = models.Application.objects.filter(creator=profile)
            if applications.exists():
                application = applications.first()
                application.status = models.ApplicationStatus.objects.get(code=models.AWAITS_VERIFICATION)
                application.save()
        except Exception as e:
            if questionnaire and isinstance(questionnaire, models.Questionnaire):
                questionnaire.delete()
            raise ValidationError({"error": f"an error occurred: {e}"})
        return questionnaire

    def update(self, instance: models.Questionnaire, validated_data: dict):
        profile = self.context['request'].profile
        if profile == instance.creator:
            try:
                info = self.context['request'].data.get('info')
                validated_data['nationality'] = models.Nationality.objects.get(pk=info['nationality']['uid'])
                family = validated_data.pop('family')
                members = family.pop('members')
                family_instance: models.Family = models.Family.objects.get(pk=instance.family.uid)
                for key, value in family.items():
                    setattr(family_instance, key, value)
                family_instance.save(snapshot=True)
                for member in members:
                    member_instance: models.FamilyMember = models.FamilyMember.objects.get(profile=member['profile'].uid)
                    address_instance = models.Address.objects.get(pk=member_instance.address.uid)
                    address = member.pop('address')
                    # info = address.pop('info')
                    # address.update({
                    #     'region': info['region'] and info['region']['uid'],
                    #     'district': info['district'] and info['district']['uid'],
                    #     'city': info['city'] and info['city']['uid'],
                    #     'locality': info['locality'] and info['locality']['uid']
                    # })
                    for key, value in address.items():
                        setattr(address_instance, key, value)
                    address_instance.save(snapshot=True)
                    for key, value in member.items():
                        setattr(member_instance, key, value)
                    member_instance.save(snapshot=True)
                id_doc = validated_data.pop('id_doc')
                id_doc_instance = IdentityDocument.objects.get(pk=instance.id_doc.uid)
                for key, value in id_doc.items():
                    setattr(id_doc_instance, key, value)
                id_doc_instance.save(snapshot=True)
                address_of_registration = validated_data.pop('address_of_registration')
                registration_instance = models.Address.objects.get(pk=instance.address_of_registration.uid)
                for key, value in address_of_registration.items():
                    setattr(registration_instance, key, value)
                registration_instance.save(snapshot=True)
                address_of_temp_reg = validated_data.pop('address_of_temp_reg', None)
                if address_of_temp_reg:
                    temp_instance = models.Address.objects.get(pk=instance.address_of_temp_reg.uid)
                    for key, value in address_of_temp_reg.items():
                        setattr(temp_instance, key, value)
                    temp_instance.save(snapshot=True)
                address_of_residence = validated_data.pop('address_of_residence')
                residence_instance = models.Address.objects.get(pk=instance.address_of_residence.uid)
                for key, value in address_of_residence.items():
                    setattr(residence_instance, key, value)
                residence_instance.save(snapshot=True)
                user_privilege_list = validated_data.pop('userprivilegelist', None)
                if user_privilege_list:
                    privileges = user_privilege_list.pop('privileges')
                    for privilege in privileges:
                        privilege_instance = models.Privilege.objects.get(
                            type=privilege['type'],
                            doc_type=privilege['doc_type'],
                        )
                        for key, value in privilege.items():
                            setattr(privilege_instance, key, value)
                        privilege_instance.save(snapshot=True)
                phone = validated_data.pop('phone')
                phone_instance = ProfilePhone.objects.get(pk=instance.phone.uid)
                for key, value in phone.items():
                    setattr(phone_instance, key, value)
                phone_instance.save(snapshot=True)
                for key, value in validated_data.items():
                    setattr(instance, key, value)
                instance.save(snapshot=True)
                profile = instance.creator
                profile.first_name = instance.first_name
                profile.last_name = instance.last_name
                profile.middle_name = instance.middle_name
                profile.email = instance.email
                profile.save()
            except Exception as e:
                raise ValidationError({"error": e})
            return instance
        else:
            raise ValidationError({"error": "access_denied"})


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
            'speciality': {
                'uid': grant.speciality.uid,
                'name': grant.speciality.name
            },
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
            'education_program': {
                'name': direction.education_program.name,
                'uid': direction.education_program.uid
            },
            'education_program_group': {
                'name': direction.education_program_group.name,
                'uid': direction.education_program_group.uid
            },
            'education_base': {
                'name': direction.education_base.name,
                'uid': direction.education_base.uid,
            },
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
                'discipline': {
                    'name': d.discipline.name,
                    'uid': d.discipline.uid,
                },
                'mark': d.mark
            } for d in result.disciplines.all()],
        }
        return info

    class Meta:
        model = models.TestResult
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField(required=False, read_only=True)

    def get_info(self, edu: models.Education):
        info = {
            'institute': {
                'name': edu.institute.name,
                'uid': edu.institute.uid
            },
            'no_institute': edu.no_institute,
            'institute_text': edu.institute_text,
            'speciality': {
                'name': edu.speciality.name,
                'uid': edu.speciality.uid,
            },
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
    max_choices = serializers.ReadOnlyField()

    class Meta:
        model = models.Application
        fields = ['uid', 'status_info', 'applicant', 'created', 'updated', 'max_choices']

    def send_on_create(self, recipient):
        today = dt.date.today().strftime("%d.%m.%Y")
        subject = 'Заявление поступило на проверку'
        message = f'Ваше заявление на поступление от {today} отправлено на проверку модератору. ' \
                  f'Ожидайте дальнейших действий'
        send_mail(subject=subject, message=message, from_email='', recipient_list=[recipient])
        return

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
            test_result = models.TestResult.objects.create(
                profile=creator,
                test_certificate=test_certificate
            )
            test_result.disciplines.add(*disciplines)
            test_result.save()
            # Международный сертификат, только если в кампании указано, что он принимаются сертифиакаты
            if my_campaign.inter_cert_foreign_lang:
                international_cert = models.InternationalCert.objects.create(
                    profile=creator,
                    **validated_data.pop('international_cert')
                )
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
            try:
                self.send_on_create(recipient=creator.email)
            except Exception as e:
                print(e)
        except Exception as e:
            if application and isinstance(application, models.Application):
                application.delete()
            raise ValidationError({"error": f"an error occurred\n{e}"})
        return application

    def update(self, instance: models.Application, validated_data: dict):
        profile = self.context['request'].user.profile
        if profile == instance.creator:
            my_campaign = profile.user.applicant.campaign
            validated_data['status'] = models.ApplicationStatus.objects.get(code=models.AWAITS_VERIFICATION)

            # Обновление предыдущего образования
            previous_education: dict = validated_data.pop('previous_education')
            education = Education.objects.get(pk=instance.previous_education.uid)
            for key, value in previous_education.items():
                setattr(education, key, value)
            education.save(snapshot=True)

            # Обновление тестов ЕНТ/КТ
            test_result: dict = validated_data.pop('test_result')
            test_cert: dict = test_result.pop('test_certificate')
            cert = models.TestCert.objects.get(pk=instance.test_result.test_certificate.uid)
            for key, value in test_cert.items():
                setattr(cert, key, value)
            cert.save(snapshot=True)
            disciplines = test_result.pop('disciplines')
            discipline: dict
            for discipline in disciplines:
                instance_discipline = instance.test_result.disciplines.get(discipline=discipline['discipline'], profile=profile)
                d = models.DisciplineMark.objects.get(pk=instance_discipline.uid)
                for key, value in discipline.items():
                    setattr(d, key, value)
                d.save(snapshot=True)

            # Обновление международного сертификата, если есть
            international_cert: dict = validated_data.pop('international_cert', None)
            if international_cert and my_campaign.inter_cert_foreign_lang:
                inter_cert_model = models.InternationalCert.objects.get(pk=instance.international_cert.uid)
                for key, value in international_cert.items():
                    setattr(inter_cert_model, key, value)
                inter_cert_model.save(snapshot=True)
            # Обновление гранта, если есть
            grant: dict = validated_data.pop('grant', None)
            if grant:
                grant_model: models.Grant = models.Grant.objects.get(pk=instance.grant.uid)
                for key, value in grant.items():
                    setattr(grant_model, key, value)
                grant_model.save(snapshot=True)
            # Обновление направлений
            directions: dict = validated_data.pop('directions', None)
            if len(directions) > my_campaign.chosen_directions_max_count:
                directions = directions[:5]
            direction: dict
            for direction in directions:
                instance_direction = models.DirectionChoice.objects.filter(
                    profile=profile,
                    education_program=direction['education_program'],
                    education_program_group=direction['education_program_group']
                )
                if instance_direction.exists():
                    instance_direction = instance_direction.first()
                    for key, value in direction.items():
                        setattr(instance_direction, key, value)
                    instance_direction.save(snapshot=True)
                else:
                    models.DirectionChoice.objects.create(**direction)
            application = super().update(instance, validated_data)
            return application
        else:
            raise ValidationError({"error": "access_denied"})


class ApplicationSerializer(ApplicationLiteSerializer):
    previous_education = EducationSerializer(required=True)
    test_result = TestResultSerializer(required=True)
    international_cert = InternationalCertSerializer(required=False, allow_null=True)
    grant = GrantSerializer(required=False, allow_null=True)
    directions = DirectionChoiceSerializer(required=True, many=True)
    questionnaire = QuestionnaireSerializer(required=False, many=False, read_only=True)

    class Meta:
        model = models.Application
        fields = '__all__'


class AdmissionDocumentSerializer(serializers.ModelSerializer):
    files_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.AdmissionDocument
        fields = '__all__'

    def validate(self, validated_data):
        return validated_data

    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def get_files_info(self, doc: models.AdmissionDocument):
        return DocScanSerializer(doc.files.all(), many=True).data
