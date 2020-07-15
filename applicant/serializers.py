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
from common.models import IdentityDocument, Comment, ReservedUID, File
from common.serializers import DocumentSerializer, DocumentTypeSerializer, FileSerializer
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
    files = FileSerializer(read_only=True, many=True, required=False)

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
        EmailTemplate.put_in_cron_queue(
            EmailTemplate.REGISTRATION_VERIFICATION,
            user.email,
            **data
        )
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
    files = FileSerializer(read_only=True, many=True, required=False)

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
        # Получить зарезервированный uid для текущего пользователя
        reserved_uid = ReservedUID.get_uid_by_user(creator.user)
        # По индексу enum получить из этого списка field_name, который соответствует каждой льготе
        for index, data in enumerate(privileges):
            privilege = models.Privilege.objects.create(
                **data,
                list=privilege_list,
                profile=creator
            )
            # Отфильтровать файлы и связать с льготой
            matching_files = File.objects.filter(
                gen_uid=reserved_uid,
                field_name=f'{models.Questionnaire.PRIVILEGE_FN}{index}'
            )
            privilege.files.set(matching_files)
            privilege.save()

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
            # Получить сканы удостоверения личности по зарезервированному uid'у и имени поля
            uid = ReservedUID.get_uid_by_user(self.context['request'].user)
            files = File.objects.filter(gen_uid=uid, field_name=models.Questionnaire.ID_DOCUMENT_FN)
            questionnaire.files.set(files)
            questionnaire.save()
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

    def update_privileges(self, data, creator, questionnaire, reserved_uid, uid=None):
        if not uid:
            user_privilege_list = models.UserPrivilegeList.objects.create(questionnaire=questionnaire, profile=creator)
        else:
            user_privilege_list = models.UserPrivilegeList.objects.get(pk=uid)
        for privilege in user_privilege_list.privileges.all():
            privilege.files.all().delete()
            privilege.delete()
        privileges = data.pop('privileges')
        for index, data in enumerate(privileges):
            data.pop('list', None)
            data.pop('profile', None)
            privilege = models.Privilege.objects.create(
                **data,
                list=user_privilege_list,
                profile=creator
            )
            matching_files = File.objects.filter(
                gen_uid=reserved_uid,
                field_name=f'{models.Questionnaire.PRIVILEGE_FN}{index}')
            privilege.files.set(matching_files)
            privilege.save()

    def update(self, instance: models.Questionnaire, validated_data: dict):
        profile = self.context['request'].user.profile
        role = profile.role
        mod_can_edit = settings.MODERATOR_CAN_EDIT and role.is_mod
        if profile == instance.creator or mod_can_edit:
            pass
        else:
            raise ValidationError({"error": "access_denied"})
        try:
            reserved_uid = ReservedUID.get_uid_by_user(profile.user)
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
                    questionnaire=instance,
                    reserved_uid=reserved_uid
                )
            instance.update(validated_data)
            files = File.objects.filter(gen_uid=reserved_uid, field_name=models.Questionnaire.ID_DOCUMENT_FN)
            instance.files.set(files)
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
    files = FileSerializer(read_only=True, many=True, required=False)

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
    files = FileSerializer(read_only=True, many=True, required=False)

    class Meta:
        model = models.InternationalCert
        fields = "__all__"


class GrantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GrantType
        fields = ['uid', 'name']


class GrantSerializer(serializers.ModelSerializer):
    files = FileSerializer(read_only=True, many=True, required=False)

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
    files = FileSerializer(read_only=True, many=True, required=False)

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

    def handle_previous_education(self, data, creator_profile, reserved_uid):
        previous_education: Education = Education.objects.create(profile=creator_profile, **data)
        files = File.objects.filter(gen_uid=reserved_uid, field_name=models.Application.EDUCATION_FN)
        previous_education.files.set(files)
        previous_education.save()
        return previous_education

    def handle_test_results(self, data, creator_profile, reserved_uid):
        # Сертификат теста ЕНТ/КТ
        test_certificate = models.TestCert.objects.create(
            profile=creator_profile,
            **data.get('test_certificate')
        )
        files = File.objects.filter(gen_uid=reserved_uid, field_name=models.Application.TEST_CERT_FN)
        test_certificate.files.set(files)
        test_certificate.save()
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

    def handle_international_certificates(self, data, creator_profile, reserved_uid):
        if len(data) == 0:
            return models.InternationalCert.objects.none()
        certs = []

        for index, international_cert in enumerate(data):
            international_cert.pop('profile', None)
            instance = models.InternationalCert.objects.create(profile=creator_profile, **international_cert)
            matching_files = File.objects.filter(
                gen_uid=reserved_uid,
                field_name=f'{models.Application.INTERNATIONAL_CERT_FN}{index}')
            instance.files.set(matching_files)
            instance.save()
            certs.append(instance)
        return certs

    def handle_grant(self, data, creator_profile, reserved_uid):
        if not data:
            return None
        grant = models.Grant.objects.create(profile=creator_profile, **data)
        files = File.objects.filter(gen_uid=reserved_uid, field_name=models.Application.GRANT_FN)
        grant.files.set(files)
        grant.save()
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
        application = None
        creator: Profile = self.context['request'].user.profile
        try:
            reserved_uid = ReservedUID.get_uid_by_user(creator.user)
            # Создатель заявления
            validated_data['creator'] = creator
            # Предыдущее образование
            validated_data['previous_education'] = self.handle_previous_education(
                data=validated_data.pop('previous_education'),
                creator_profile=creator,
                reserved_uid=reserved_uid
            )
            # Грант
            validated_data['grant'] = self.handle_grant(
                data=validated_data.pop('grant', None),
                creator_profile=creator,
                reserved_uid=reserved_uid
            )
            # Результат теста ЕНТ/КТ
            unpassed_test = validated_data.get('unpassed_test')
            if unpassed_test:
                validated_data.pop('test_result', None)
            else:
                validated_data['test_result'] = self.handle_test_results(
                    data=validated_data.pop('test_result'),
                    creator_profile=creator,
                    reserved_uid=reserved_uid
                )
            # Международные сертификаты
            international_certs = self.handle_international_certificates(
                data=validated_data.pop('international_certs', []),
                creator_profile=creator,
                reserved_uid=reserved_uid
            )
            # Направления
            directions = self.handle_directions(validated_data.pop('directions'), creator)
            application = models.Application.objects.create(**validated_data)
            application.international_certs.set(international_certs)
            application.directions.set(directions)
            application.save()
            try:
                self.send_on_create(recipient=creator.user.email)
            except Exception as e:
                print(e)
        except Exception as e:
            if application and isinstance(application, models.Application):
                application.delete()
            raise ValidationError({"error": f"an error occurred\n{e}"})
        return application

    def update(self, instance: models.Application, validated_data: dict):
        profile = self.context['request'].user.profile
        mod_can_edit = settings.MODERATOR_CAN_EDIT and profile.role.is_mod
        # Доступ к изменению анкеты
        if not (profile == instance.creator or mod_can_edit):
            raise ValidationError({"error": "access_denied"})
        # Резервированный UID берется от текущего пользователя. Им может быть модератор.
        reserved_uid = ReservedUID.get_uid_by_user(profile.user)
        # ==============================================================================================================
        # Предыдущее образовании обязательно должно быть в запросе
        previous_education: dict = validated_data.pop('previous_education')
        education: Education = Education.objects.get(pk=instance.previous_education.uid)
        education.update(previous_education)
        # Если модератор загрузил файлы, например у абитуриента не было с собой аттестата/диплома,
        # но передал скан модератору позже. Модератор может загрузить скан от имени абитуриента
        files = File.objects.filter(gen_uid=reserved_uid, field_name=models.Application.EDUCATION_FN)
        education.files.set(files)
        education.save(snapshot=True)
        # ==============================================================================================================
        # Прошел/не прошел тест ЕНТ/КТ
        # unpassed_test - tсли true - то не прошел, иначе прошел
        unpassed_test = validated_data.get('unpassed_test')
        test_result = validated_data.pop('test_result', None)
        # Если до этого был заполнен результат теста и пришли поправки, то обновить результат теста
        if instance.test_result and test_result:
            test_certificate: models.TestCert = models.TestCert.objects.get(pk=instance.test_result.test_certificate.pk)
            test_certificate.update(test_result.get('test_certificate'))
            test_cert_files = File.objects.filter(gen_uid=reserved_uid, field_name=models.Application.TEST_CERT_FN)
            test_certificate.files.set(test_cert_files)
            test_certificate.save(snapshot=True)
            instance.test_result.disciplines.all().delete()
            new_disciplines = models.DisciplineMark.objects.bulk_create([
                models.DisciplineMark(**discipline) for discipline in test_result.get('disciplines')
            ])
            instance.test_result.disciplines.set(new_disciplines)
            instance.test_result.save(snapshot=True)
        # Если же сначала пометил, что не прошел тест, а потом снял эту отметку и заполнил данные о результате теста,
        # то создать и прикрепить к заявлению
        elif instance.unpassed_test and not instance.test_result and not unpassed_test:
            test_result = self.handle_test_results(
                data=test_result,
                creator_profile=instance.creator,
                reserved_uid=reserved_uid
            )
            instance.test_result = test_result
            instance.save()
        # ==============================================================================================================
        # Международные сертификаты
        is_cert_holder: bool = validated_data.get('is_cert_holder', False)
        international_certs: list = validated_data.pop('international_certs', [])
        # Если есть международные сертификаты и кампания их принимает
        if is_cert_holder and len(international_certs) > 0:
            # Просто удалить и создать новые сертификаты
            instance.international_certs.all().delete()
            international_certs = self.handle_international_certificates(
                data=international_certs,
                creator_profile=instance.creator,
                reserved_uid=reserved_uid
            )
            instance.international_certs.set(international_certs)
            instance.save()
        # ==============================================================================================================
        # Проверка на грант
        is_grant_holder: bool = validated_data.get('is_grant_holder', False)
        grant: dict = validated_data.pop('grant', None)
        # Если раньше по каким-то причинам указал, что не грантник, а потом добавил информацию о гранте,
        # то просто создать грант. Иначе обновить текущий грант и привязать новые сканы гранта
        if not instance.is_grant_holder and is_grant_holder and grant:
            grant_model = self.handle_grant(data=grant, creator_profile=instance.creator, reserved_uid=reserved_uid)
            instance.grant = grant_model
            instance.save()
        else:
            grant_model: models.Grant = models.Grant.objects.get(pk=instance.grant.uid)
            grant_model.update(grant)
            grant_files = File.objects.filter(gen_uid=reserved_uid, field_name=models.Application.GRANT_FN)
            grant_model.files.set(grant_files)
            grant_model.save(snapshot=True)
        # ==============================================================================================================
        # Сделать с выбранными направлениями то же самое, что и с международ. сертификатами - удалить и создать по новой
        # TODO сделать проверку на соответствие с группой образовательных программ в гранте и первом направлении
        #  в самом начале запроса на обновление заявления
        instance.directions.all().delete()
        directions = models.OrderedDirection.objects.bulk_create([
            models.OrderedDirection(**direction) for direction in validated_data.pop('directions')
        ])
        instance.directions.set(directions)
        instance.save(snapshot=True)
        # ==============================================================================================================
        application = super().update(instance, validated_data)
        return application


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
    type = serializers.SerializerMethodField(read_only=True)
    files = FileSerializer(read_only=True, many=True, required=False)

    def get_type(self, document: models.AdmissionDocument):
        try:
            return document.document_1c.type.name
        except Exception:
            return

    class Meta:
        model = models.AdmissionDocument
        fields = '__all__'

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user.profile
        order = self.context['request'].data.get('order')
        reserved_uid = ReservedUID.get_uid_by_user(validated_data['creator'].user)
        field_name = f'{models.AdmissionDocument.FIELD_NAME}{order}'
        files = File.objects.filter(gen_uid=reserved_uid, field_name=field_name)
        instance: models.AdmissionDocument = super().create(validated_data)
        instance.files.set(files)
        instance.save()
        return instance

    def update(self, instance: models.AdmissionDocument, validated_data):
        profile = self.context['request'].user.profile
        mod_can_edit = profile.role.is_mod and settings.MODERATOR_CAN_EDIT
        if not (profile == instance.creator or mod_can_edit):
            raise ValidationError({'error': 'access_denied'})
        reserved_uid = ReservedUID.get_uid_by_user(profile.user)
        order = self.context['request'].data.get('order')
        field_name = f'{models.AdmissionDocument.FIELD_NAME}{order}'
        files = File.objects.filter(gen_uid=reserved_uid, field_name=field_name)
        instance.files.set(files)
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
    files = serializers.SerializerMethodField(required=False)

    def get_files(self, d1c: models.Document1C):
        try:
            profile = self.context['request'].user.profile
            admission_documents = d1c.document.filter(creator=profile)
            return AdmissionDocumentSerializer(admission_documents, many=True).data
        except:
            return []

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
