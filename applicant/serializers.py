import datetime as dt
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.db.models import Max
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import get_language
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from common.models import IdentityDocument, Comment
from common.serializers import DocumentSerializer, DocumentTypeSerializer
from mail.models import EmailTemplate
from portal.local_settings import EMAIL_HOST_USER
from portal_users.serializers import ProfilePhoneSerializer
from portal_users.models import Profile, Role, ProfilePhone
from organizations.models import Education
from .token import token_generator
from . import models


class PrivilegeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PrivilegeType
        fields = ['uid', 'name']


class PrivilegeSerializer(serializers.ModelSerializer):
    doc = DocumentSerializer(source='document', read_only=True, required=False)

    class Meta:
        model = models.Privilege
        fields = '__all__'


class UserPrivilegeListSerializer(serializers.ModelSerializer):
    privileges = PrivilegeSerializer(many=True, required=True)

    class Meta:
        model = models.UserPrivilegeList
        exclude = ['questionnaire']


class DocumentReturnMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentReturnMethod
        fields = ['uid', 'name']


class FamilyMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FamilyMembership
        fields = ['uid', 'name']


class AddressClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AddressClassifier
        fields = ['uid', 'name']


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
        fields = ['uid', 'name']


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

    def send_verification_email(self, user: User, password: str):
        data = {
            'username': user.username,
            'password': password,
            'domain': get_current_site(self.context['request']).domain,
            'lang': get_language() or 'ru',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user)
        }
        EmailTemplate.put_in_cron_queue('REGISTRATION_VERIFICATION', user.email, **data)
        return

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
            self.send_verification_email(user, raw_password)
            # Возвращаем экземпляр абитуриента
            return applicant
        except Exception as e:
            user = applicant.user
            if user:
                user.delete()
            applicant.delete()
            raise ValidationError({"error": e})


class IdentityDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IdentityDocument
        exclude = ['profile']


class QuestionnaireLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Questionnaire
        fields = ['uid', 'creator']


class QuestionnaireSerializer(serializers.ModelSerializer):
    family = FamilySerializer(required=False)
    id_doc = IdentityDocumentSerializer(required=True)
    address_of_registration = AddressSerializer(required=False)
    address_of_temp_reg = AddressSerializer(required=False, allow_null=True)
    address_of_residence = AddressSerializer(required=True)
    privilege_list = UserPrivilegeListSerializer(required=False, many=False)
    phone = ProfilePhoneSerializer(required=True)
    document = DocumentSerializer(source='id_document', required=False)

    class Meta:
        model = models.Questionnaire
        exclude = ['creator']

    def validate(self, validated_data: dict):
        address_matches: int = validated_data.get('address_matches')
        address_of_temp_reg: dict = validated_data.pop('address_of_temp_reg', None)
        temp_reg_present = address_of_temp_reg and any(address_of_temp_reg.values())
        if address_matches == models.Questionnaire.MATCH_TMP and not temp_reg_present:
            raise ValidationError({"error": "temp_addr_not_present"})
        is_orphan = validated_data.get('is_orphan')
        if is_orphan:
            validated_data.pop('family', None)
        else:
            family: dict = validated_data.pop('family')
            members: list = family.pop('members')
            members_with_temp_reg = any(map(lambda member: member['address_matches'] == models.Address.TMP, members))
            if members_with_temp_reg and not temp_reg_present:
                raise ValidationError({"error": "member_addr_empty_temp_reg"})
            family['members'] = members
            validated_data['family'] = family
        address_of_registration = validated_data.pop('address_of_registration')
        address_of_residence = validated_data.pop('address_of_residence')
        if address_matches == models.Questionnaire.MATCH_REG:
            address_of_residence = address_of_registration
        elif address_matches == models.Questionnaire.MATCH_TMP:
            address_of_residence = address_of_temp_reg
        elif address_matches == models.Questionnaire.MATCH_RES:
            pass
        address_of_registration['type'] = models.Address.REG
        if temp_reg_present:
            address_of_temp_reg['type'] = models.Address.TMP
        address_of_residence['type'] = models.Address.RES
        is_privileged = validated_data.get('is_privileged')
        if not is_privileged:
            validated_data.pop('privilege_list', None)
        validated_data['address_of_registration'] = address_of_registration
        validated_data['address_of_temp_reg'] = address_of_temp_reg if temp_reg_present else None
        validated_data['address_of_residence'] = address_of_residence
        return validated_data

    def create_family(self, family_data, profile, reg_addr_uid, tmp_addr_uid, res_addr_uid):
        members = family_data.pop('members')
        family = models.Family.objects.create(**family_data, profile=profile)
        for member in members:
            member['family'] = family
            email = member['email']
            user_match = User.objects.filter(username=email)
            if user_match.exists():
                user = user_match.first()
            else:
                user = User.objects.create(username=email, email=email)
                user.set_password(member['email'])
                user.save()
            member_profile_match = Profile.objects.filter(user=user)
            if member_profile_match.exists():
                member_profile = member_profile_match.first()
            else:
                member_profile = Profile.objects.create(
                    first_name=member['first_name'],
                    last_name=member['last_name'],
                    middle_name=member['middle_name'],
                    user=user
                )
            member['profile'] = member_profile
            address_matches = member['address_matches']
            if address_matches == models.FamilyMember.MATCH_REG:
                registration_copy = models.Address.objects.filter(pk=reg_addr_uid).first()
                registration_copy.pk = None
                registration_copy.save()
                member['address'] = registration_copy
            elif address_matches == models.FamilyMember.MATCH_TMP:
                temporary_copy = models.Address.objects.filter(pk=tmp_addr_uid).first()
                temporary_copy.pk = None
                temporary_copy.save()
                member['address'] = temporary_copy
            elif address_matches == models.FamilyMember.MATCH_RES:
                residence_copy = models.Address.objects.filter(pk=res_addr_uid).first()
                residence_copy.pk = None
                residence_copy.save()
                member['address'] = residence_copy
            elif address_matches == models.FamilyMember.MATCH_NOT:
                address = models.Address.objects.create(**member['address'], profile=profile)
                member['address'] = address
            member_match = models.FamilyMember.objects.filter(profile=member_profile)
            if member_match.exists():
                member_instance = member_match.first()
                member_instance.update(member)
            else:
                models.FamilyMember.objects.create(**member)
        return family

    def create_privileges(self, privilege_list, creator, questionnaire):
        privileges = privilege_list.pop('privileges')
        privilege_list = models.UserPrivilegeList.objects.create(
            **privilege_list,
            profile=creator,
            questionnaire=questionnaire
        )
        for privilege in privileges:
            models.Privilege.objects.create(
                **privilege,
                list=privilege_list,
                profile=creator
            )

    def create(self, validated_data):
        creator = self.context['request'].user.profile
        questionnaire = models.Questionnaire.objects.filter(creator=creator)
        if questionnaire.exists():
            return questionnaire.first()
        else:
            questionnaire = None
        try:
            # Сначала нужно разобраться с адресами
            # Адрес прописки/регистрации
            address_of_registration = models.Address.objects.create(
                **validated_data.pop('address_of_registration'),
                profile=creator,
            )
            # Временный адрес (для жителей Казахстана)
            address_of_temp_reg = validated_data.pop('address_of_temp_reg')
            if address_of_temp_reg:
                address_of_temp_reg = models.Address.objects.create(
                    **address_of_temp_reg,
                    profile=creator
                )
            # Фактический адрес проживания
            address_of_residence = models.Address.objects.create(
                **validated_data.pop('address_of_residence'),
                profile=creator
            )
            # Обработка данных семьи и ее членов
            is_orphan = validated_data.get('is_orphan', False)
            if not is_orphan:
                family_data = validated_data.pop('family')
                family = self.create_family(
                    family_data=family_data,
                    profile=creator,
                    reg_addr_uid=address_of_registration.pk,
                    tmp_addr_uid=address_of_temp_reg and address_of_temp_reg.pk,
                    res_addr_uid=address_of_residence.pk
                )
            else:
                family = None
            # Докумуент удостоверяющий личность
            id_doc = IdentityDocument.objects.create(**validated_data.pop('id_doc'))
            # Телефон
            phone = ProfilePhone.objects.create(**validated_data.pop('phone'))
            # Проверка на привилегии
            is_privileged = validated_data.get('is_privileged', False)
            privilege_list = validated_data.pop('privilege_list', None)
            questionnaire = models.Questionnaire.objects.create(
                creator=creator,
                family=family,
                address_of_registration=address_of_registration,
                address_of_temp_reg=address_of_temp_reg,
                address_of_residence=address_of_residence,
                id_doc=id_doc,
                phone=phone,
                **validated_data
            )
            if is_privileged:
                self.create_privileges(
                    privilege_list=privilege_list,
                    creator=creator,
                    questionnaire=questionnaire
                )
        except Exception as e:
            if questionnaire and isinstance(questionnaire, models.Questionnaire):
                questionnaire.delete()
            raise ValidationError({'error on create': e})
        return questionnaire

    def update_family(self, uid, data):
        members = data.pop('members')
        family: models.Family = models.Family.objects.get(pk=uid)
        family.update(data)
        family.save(snapshot=True)
        for member in members:
            member_instance = models.FamilyMember.objects.get(profile=member['profile'].uid)
            address_instance = models.Address.objects.get(pk=member_instance.address.uid)
            address = member.pop('address')
            address_instance.update(address)
            address_instance.save(snapshot=True)
            member_instance.update(member)
            member_instance.save(snapshot=True)

    def update_id_doc(self, uid, data):
        id_doc = IdentityDocument.objects.get(pk=uid)
        id_doc.update(data)
        id_doc.save(snapshot=True)

    def update_phone(self, uid, data):
        phone_instance = ProfilePhone.objects.get(pk=uid)
        phone_instance.update(data)
        phone_instance.save(snapshot=True)

    def update_registration_address(self, uid, data):
        registration_address = models.Address.objects.get(pk=uid)
        registration_address.update(data)
        registration_address.save(snapshot=True)

    def update_temporary_registration_address(self, uid, data):
        temporary_address = models.Address.objects.get(pk=uid)
        temporary_address.update(data)
        temporary_address.save(snapshot=True)

    def update_residence_address(self, uid, data):
        residence_address = models.Address.objects.get(pk=uid)
        residence_address.update(data)
        residence_address.save(snapshot=True)

    def update_privileges(self, data, creator, questionnaire, uid=None,):
        if not uid:
            print("not uid")
            user_privilege_list = models.UserPrivilegeList.objects.create(questionnaire=questionnaire, profile=creator)
        else:
            print("existing")
            user_privilege_list = models.UserPrivilegeList.objects.get(pk=uid)
            user_privilege_list.privileges.all().delete()
        privileges = data.pop('privileges')
        for privilege in privileges:
            p = models.Privilege.objects.create(**privilege)
            p.profile = creator
            p.list = user_privilege_list
            p.save()

    def update(self, instance: models.Questionnaire, validated_data: dict):
        profile = self.context['request'].user.profile
        role = profile.role
        mod_can_edit = settings.MODERATOR_CAN_EDIT and role.is_mod
        if profile == instance.creator or mod_can_edit:
            try:
                self.update_registration_address(
                    uid=instance.address_of_registration.pk,
                    data=validated_data.pop('address_of_registration')
                )
                tmp_address: dict = validated_data.pop('address_of_temp_reg', None)
                if tmp_address and any(tmp_address.values()):
                    self.update_temporary_registration_address(
                        uid=instance.address_of_temp_reg.pk,
                        data=tmp_address
                    )
                self.update_residence_address(
                    uid=instance.address_of_residence.pk,
                    data=validated_data.pop('address_of_residence')
                )
                is_orphan = validated_data.get('is_orphan')
                if instance.is_orphan and not is_orphan:
                    family = self.create_family(
                        family_data=validated_data.pop('family'),
                        profile=profile,
                        reg_addr_uid=instance.address_of_registration.pk,
                        tmp_addr_uid=instance.address_of_temp_reg and instance.address_of_temp_reg.pk,
                        res_addr_uid=instance.address_of_residence.pk
                    )
                    instance.family = family
                    instance.save()
                if not instance.is_orphan:
                    self.update_family(uid=instance.family.pk, data=validated_data.pop('family'))
                self.update_id_doc(uid=instance.id_doc.pk, data=validated_data.pop('id_doc'))
                self.update_phone(uid=instance.phone.pk, data=validated_data.pop('phone'))
                is_privileged = validated_data.get('is_privileged')
                if not instance.is_privileged and is_privileged:
                    self.create_privileges(
                        validated_data.pop('privilege_list'),
                        creator=profile,
                        questionnaire=instance
                    )
                if instance.is_privileged:
                    privileges = validated_data.pop('privilege_list', None)
                    self.update_privileges(
                        uid=instance.privilege_list.pk,
                        data=privileges,
                        creator=profile,
                        questionnaire=instance
                    )
                instance.update(validated_data)
                instance.save(snapshot=True)
                Profile.objects.filter(pk=profile.pk).update(
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    middle_name=instance.middle_name,
                    email=instance.email
                )
                return instance
            except Exception as e:
                raise ValidationError({"got error on update": e})
        else:
            raise ValidationError({"error": "access_denied"})

    def save_history_log(self, creator_profile, status, text):
        comment = Comment.objects.create(
            text=text,
            creator=creator_profile,
            content_type=self
        )
        models.ApplicationStatusChangeHistory.objects.create(
            author=creator_profile,
            status=status,
            comment=comment,
        )


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicationStatus
        fields = ['uid', 'name']


class CampaignStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CampaignStage
        fields = "__all__"


class RecruitmentPlanSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()

    def get_info(self, plan: models.RecruitmentPlan):
        return {
            "prep_level": getattr(plan.prep_level, 'name', ''),
            "study_form": getattr(plan.study_form, 'name', ''),
            "language": getattr(plan.language, 'name', ''),
            "admission_basis": getattr(plan.admission_basis, 'name', ''),
            "education_program_group": f'{getattr(plan.education_program_group, "code", "")} {getattr(plan.education_program_group, "name", "")}',
            "education_program": f'{getattr(plan.education_program, "code", "")} {getattr(plan.education_program, "name", "")}',
            "study_period": getattr(plan.study_period, "repr_name", ""),
            "test_form": getattr(plan.entrance_test_form, "name", ""),
        }

    class Meta:
        model = models.RecruitmentPlan
        fields = "__all__"


class DisciplineMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DisciplineMark
        fields = "__all__"


class TestCertSerializer(serializers.ModelSerializer):
    doc = DocumentSerializer(read_only=True, source='document')

    class Meta:
        model = models.TestCert
        fields = "__all__"


class LanguageProficiencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LanguageProficiency
        fields = ['uid', 'name', 'code']


class InternationalCertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InternationalCertType
        fields = ['uid', 'name']


class InternationalCertSerializer(serializers.ModelSerializer):
    doc = DocumentSerializer(read_only=True, source='document')

    class Meta:
        model = models.InternationalCert
        fields = "__all__"


class GrantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GrantType
        fields = ['uid', 'name']


class GrantSerializer(serializers.ModelSerializer):
    doc = DocumentSerializer(source='document', read_only=True)

    class Meta:
        model = models.Grant
        fields = "__all__"


class TestResultSerializer(serializers.ModelSerializer):
    disciplines = DisciplineMarkSerializer(required=True, many=True)
    test_certificate = TestCertSerializer(required=True)

    class Meta:
        model = models.TestResult
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    doc = DocumentSerializer(read_only=True, source='document')

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
        send_mail(subject=subject, message=message, from_email=EMAIL_HOST_USER, recipient_list=[recipient])
        return

    def handle_previous_education(self, data, creator_profile):
        previous_education = Education.objects.create(profile=creator_profile, **data)
        return previous_education

    def handle_test_results(self, data, creator_profile):
        # Сертификат теста ЕНТ/КТ
        test_certificate = models.TestCert.objects.create(
            profile=creator_profile,
            **data.get('test_certificate')
        )
        # Пройденные дисциплины на тесте
        disciplines = models.DisciplineMark.objects.bulk_create([
            models.DisciplineMark(profile=creator_profile, **discipline) for discipline in data.get('disciplines')
        ])
        # Результат теста
        test_result = models.TestResult.objects.create(
            profile=creator_profile,
            test_certificate=test_certificate
        )
        test_result.disciplines.set(disciplines)
        test_result.save()
        return test_result

    def handle_international_certificates(self, data, creator_profile):
        if len(data) == 0:
            return models.InternationalCert.objects.none()
        certs = []
        for cert in data:
            certs.append(models.InternationalCert.objects.create(profile=creator_profile, **cert))
        return certs

    def handle_grant(self, data, creator_profile):
        if not data:
            return None
        grant = models.Grant.objects.create(profile=creator_profile, **data)
        return grant

    def handle_directions(self, data, creator_profile):
        directions = models.OrderedDirection.objects.bulk_create([
            models.OrderedDirection(**direction) for direction in data
        ])
        return directions

    def save_history_log(self, creator_profile, status, text=""):
        comment = Comment.objects.create(
            text=text,
            creator=creator_profile,
            content_type=self
        )
        models.ApplicationStatusChangeHistory.objects.create(
            author=creator_profile,
            status=status,
            comment=comment,
        )

    def create(self, validated_data: dict):
        creator: Profile = self.context['request'].user.profile
        try:
            data = {
                'previous_education': self.handle_previous_education(validated_data.pop('previous_education'), creator),
                'grant': self.handle_grant(validated_data.pop('grant', None), creator),
                'creator': creator
            }
            unpassed_test = validated_data.get('unpassed_test')
            if unpassed_test:
                validated_data.pop('test_result', None)
            else:
                data['test_result'] = self.handle_test_results(validated_data.pop('test_result'), creator)
            validated_data.update(data)
            international_certs = self.handle_international_certificates(
                validated_data.pop('international_certs', []),
                creator
            )
            directions = self.handle_directions(validated_data.pop('directions'), creator)
            application = models.Application.objects.create(**validated_data)
            application.international_certs.set(international_certs)
            application.directions.set(directions)
            application.save()
            # У меня не создается заявление из-за этого
            # self.save_history_log(
            #     creator_profile=creator,
            #     status=status,
            #     # Посмотри на переменную status сверху и узнай есть ли у нее атрибут name.
            #     text=f"Заявление создано со статусом {data['status'].name}"
            # )
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
        role = profile.role
        mod_can_edit = settings.MODERATOR_CAN_EDIT and role.is_mod
        if profile == instance.creator or mod_can_edit:
            my_campaign = profile.user.applicant.campaign
            previous_education: dict = validated_data.pop('previous_education')
            education = Education.objects.get(pk=instance.previous_education.uid)
            education.update(previous_education)
            education.save(snapshot=True)
            unpassed_test = validated_data.get('unpassed_test')
            if not unpassed_test:
                try:
                    tr = validated_data.pop('test_result')
                    ts = tr.get('test_certificate')
                    disciplines_from_val_data = tr.get('disciplines')
                    if disciplines_from_val_data.__len__() <= 0:
                        raise Exception
                except:
                    raise ValidationError({"error": "test_result_not_specified"})
                if instance.test_result:
                    test_result: dict = tr
                    test_cert: dict = ts
                    cert = models.TestCert.objects.get(pk=instance.test_result.test_certificate.uid)
                    cert.update(test_cert)
                    cert.save(snapshot=True)
                    instance.test_result.disciplines.all().delete()
                    new_disciplines = models.DisciplineMark.objects.bulk_create([
                    models.DisciplineMark(**discipline) for discipline in disciplines_from_val_data])
                    instance.test_result.disciplines.set(new_disciplines)
                    instance.test_result.save(snapshot=True)
                else:
                    test_result = tr
                    test_certificate = models.TestCert.objects.create(profile=profile,**ts)
                    disciplines = models.DisciplineMark.objects.bulk_create([models.DisciplineMark(profile=profile, **discipline) for discipline in disciplines_from_val_data])
                    # Результат теста
                    test_result = models.TestResult.objects.create(profile=profile,test_certificate=test_certificate)
                    test_result.disciplines.set(disciplines)
                    test_result.save()
                    instance.test_result = test_result
                    instance.save()


            is_cert_holder = bool = validated_data.get('is_cert_holder', False)
            international_certs: list = validated_data.pop('international_certs', [])
            if is_cert_holder and my_campaign.inter_cert_foreign_lang:
                instance.international_certs.all().delete()
                international_certs = models.InternationalCert.objects.bulk_create([
                    models.InternationalCert(**cert) for cert in international_certs
                ])
                instance.international_certs.set(international_certs)
                instance.save()
            is_grant_holder: bool = validated_data.get('is_grant_holder', False)
            grant: dict = validated_data.pop('grant', None)
            if not instance.is_grant_holder and is_grant_holder:
                grant_model = models.Grant.objects.create(**grant, profile=profile)
                grant_model.application_set.add(instance)
                grant_model.save()
            elif is_grant_holder:
                grant_model: models.Grant = models.Grant.objects.get(pk=instance.grant.uid)
                grant_model.update(grant)
                grant_model.save(snapshot=True)
            instance.directions.all().delete()
            directions = models.OrderedDirection.objects.bulk_create([
                models.OrderedDirection(**direction) for direction in validated_data.pop('directions')
            ])
            instance.directions.set(directions)
            instance.save(snapshot=True)
            application = super().update(instance, validated_data)
            # self.save_history_log(
            #     creator_profile=instance.creator,
            #     status=instance.status,
            #     text="В заявление внесены изменения"
            # )
            return application
        else:
            raise ValidationError({"error": "access_denied"})


class OrderedDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderedDirection
        fields = ['plan', 'order_number']


class ApplicationSerializer(ApplicationLiteSerializer):
    previous_education = EducationSerializer(required=True)
    test_result = TestResultSerializer(required=False)
    international_certs = InternationalCertSerializer(required=False, many=True)
    grant = GrantSerializer(required=False, allow_null=True)
    directions = OrderedDirectionSerializer(required=True, many=True)

    class Meta:
        model = models.Application
        fields = '__all__'


class AdmissionDocumentSerializer(serializers.ModelSerializer):
    doc = DocumentSerializer(source='document', read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    def get_type(self, document: models.AdmissionDocument):
        try:
            return document.document_1c.type.name
        except Exception:
            return

    class Meta:
        model = models.AdmissionDocument
        fields = '__all__'

    def validate(self, validated_data):
        return validated_data

    def create(self, validated_data):
        creator = validated_data.get('creator')
        return super().create(validated_data)

    def update(self, instance: models.AdmissionDocument, validated_data):
        new_files = validated_data.pop('files')
        instance.document.files.clear()
        instance.document.files.set(new_files)
        instance.save()
        return super().update(instance, validated_data)


class OrderedDirectionsForModerator(serializers.ModelSerializer):
    class Meta:
        model = models.OrderedDirection
        fields = [
            'uid',
            'order_number',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['education_program'] = instance.plan.education_program.name
        data['language'] = instance.plan.language.name

        return data


class ModeratorSerializer(serializers.ModelSerializer):
    directions = OrderedDirectionsForModerator(required=True, many=True)
    status = serializers.CharField()

    class Meta:
        model = models.Application
        fields = [
            'uid',
            'directions',
            'status',
            'status_action',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['full_name'] = instance.creator.full_name
        try:
            questionnairies = models.Questionnaire.objects.get(creator=instance.creator)
            data['iin'] = questionnairies.iin  # iin В Казахстане означает индивидуальный идентификационный номер
            data['citizenship'] = questionnairies.citizenship.name
            if questionnairies.address_of_registration is not None:
                data['address_of_registration'] = questionnairies.address_of_registration.name
            else:
                data['address_of_registration'] = ""
            if questionnairies.address_of_residence is not None:
                data['address_of_residence'] = questionnairies.address_of_residence.name
            else:
                data['address_of_residence'] = ""
            if questionnairies.address_of_temp_reg is not None:
                data['address_of_temp_reg'] = questionnairies.address_of_temp_reg.name
            else:
                data['address_of_temp_reg'] = ""

            family_members = models.FamilyMember.objects.filter(family=questionnairies.family)
            data['family_members'] = FamilyMemberForModerator(family_members, many=True).data

        except models.Questionnaire.DoesNotExist:
            data['iin'] = ""
            data['address_of_registration'] = ""
            data['address_of_residence'] = ""
            data['address_of_temp_reg'] = ""
            data['family_members'] = []

        return data

class ModeratorQuestionnaireSerializer(serializers.ModelSerializer):
    directions = OrderedDirectionsForModerator(required=True, many=True,allow_null=True)
    status = serializers.CharField(allow_null=True)

    class Meta:
        model = models.Questionnaire
        fields = [
            'uid',
            'status',
            'directions',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['full_name'] = instance.creator.full_name
        try:
            questionnairies = models.Questionnaire.objects.get(creator=instance.creator)
            data['iin'] = questionnairies.iin  # iin В Казахстане означает индивидуальный идентификационный номер
            data['citizenship'] = questionnairies.citizenship.name
            if questionnairies.address_of_registration is not None:
                data['address_of_registration'] = questionnairies.address_of_registration.name
            else:
                data['address_of_registration'] = ""
            if questionnairies.address_of_residence is not None:
                data['address_of_residence'] = questionnairies.address_of_residence.name
            else:
                data['address_of_residence'] = ""
            if questionnairies.address_of_temp_reg is not None:
                data['address_of_temp_reg'] = questionnairies.address_of_temp_reg.name
            else:
                data['address_of_temp_reg'] = ""

            family_members = models.FamilyMember.objects.filter(family=questionnairies.family)
            data['family_members'] = FamilyMemberForModerator(family_members, many=True).data

        except models.Questionnaire.DoesNotExist:
            data['iin'] = ""
            data['address_of_registration'] = ""
            data['address_of_residence'] = ""
            data['address_of_temp_reg'] = ""
            data['family_members'] = []

        return data

class FamilyMemberForModerator(serializers.ModelSerializer):
    address = serializers.CharField()

    class Meta:
        model = models.FamilyMember
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'workplace',
            'phone',
            'address',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['membership'] = instance.membership.name

        return data


class Document1CSerializer(serializers.ModelSerializer):
    type = DocumentTypeSerializer(read_only=True)
    document = AdmissionDocumentSerializer()

    class Meta:
        model = models.Document1C
        fields = '__all__'


class CommentsForHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'text',
            'creator'
        ]


class ApplicationChangeHistorySerializer(serializers.ModelSerializer):
    status = serializers.CharField()
    comment = CommentsForHistorySerializer(required=True)

    class Meta:
        model = models.ApplicationStatusChangeHistory
        fields = [
            'uid',
            'created',
            'status',
            'comment',
        ]


class ApplicantMyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Application
        fields = [
            'uid'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['status'] = instance.status and instance.status.name_ru
        data['status_code'] = instance.status and instance.status.code
        last_comment = models.ApplicationStatusChangeHistory.objects.filter(author=instance.creator).order_by(
            'created').last()
        if last_comment is not None:
            data['comment'] = last_comment.comment.text
        else:
            data['comment'] = ""
        return data
