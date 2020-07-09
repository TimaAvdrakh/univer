import datetime as dt
import logging
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q, prefetch_related_objects
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet
from common.paginators import CustomPagination
from univer_admin.permissions import IsAdminOrReadOnly
from portal_users.models import Profile
from . import models
from . import serializers
from portal.curr_settings import applicant_application_statuses
from .token import token_generator


logger = logging.getLogger('django')


# Активация аккаунта
def activate(request, uidb64, token):
    user = None
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        return JsonResponse({"message": "error", "status": "ERR_ACTIVATION", "error": str(e)})
    if user and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return JsonResponse({"message": "activated", "status": "ACTIVATED", "error": None})
    else:
        return JsonResponse({"message": "noUser", "status": "NOT_FOUND", "error": None})


class ApplicantViewSet(ModelViewSet):
    queryset = models.Applicant.objects.all()
    serializer_class = serializers.ApplicantSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        import datetime as dt
        validated_data = request.data
        user = User.objects.filter(email=validated_data['email'])
        applicant = models.Applicant.objects.filter(email=validated_data['email'])
        if user.exists() or applicant.exists():
            raise ValidationError({
                'error': {
                    "message": "email_exists"
                }
            })
        id_doc = models.IdentityDocument.objects.filter(number=validated_data["doc_num"])
        doc_num = models.Applicant.objects.filter(doc_num=validated_data['doc_num'])
        if id_doc.exists() or doc_num.exists():
            raise ValidationError({
                "error": {
                    "message": "id_exists"
                }
            })
        if len(validated_data["doc_num"]) > 16:
            raise ValidationError({
                "error": {
                    "message": "id_number_long"
                }
            })
        campaign_type = validated_data.get('campaign_type')
        today = dt.date.today()
        campaigns = models.AdmissionCampaign.objects.filter(
            type=campaign_type,
            is_active=True,
            year=today.year,
            start_date__lte=today,
            end_date__gte=today
        )
        if campaigns.exists():
            validated_data['campaign'] = str(campaigns.first().uid)
        else:
            raise ValidationError({
                "error": {
                    "message": "no_campaign"
                }
            })
        # Проверка этапов приемной кампан
        campaign: models.AdmissionCampaign = campaigns.first()
        stages = campaign.stages.filter(
            prep_level=validated_data['prep_level'],
            start_date__lte=today,
            end_date__gte=today,
        )
        if not stages.exists():
            raise ValidationError({
                "error": {
                    "message": "no_stages"
                }
            })
        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_path='my-prep-level', url_name='applicant_prep_level')
    def applicant_prep_level(self, request, pk=None):
        user = self.request.user
        if hasattr(user, 'applicant'):
            return Response(data={'prep_level': user.applicant.prep_level.name}, status=HTTP_200_OK)
        else:
            return Response()

    @action(methods=['post'], detail=False, url_path='campaign-types', url_name='campaign_types')
    def get_campaign_types(self, request, pk=None):
        prep_level = request.data.get('prep_level')
        campaign_types = models.AdmissionCampaignType.objects.filter(prep_levels=prep_level)
        return Response(data=serializers.AdmissionCampaignTypeSerializer(campaign_types, many=True).data,
                        status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='search', url_name='search')
    def search(self, request, pk=None):
        from portal_users.serializers import ProfileLiteSerializer
        name = request.query_params.get('name', None)
        if name:
            dataset = ProfileLiteSerializer(
                Profile.objects.filter(user__applicant__isnull=False).filter(
                    Q(first_name__icontains=name)
                    | Q(last_name__icontains=name)
                    | Q(middle_name__icontains=name)
                ).distinct()[:20],
                many=True
            ).data
            return Response(data=dataset, status=HTTP_200_OK)
        else:
            return Response(data=[], status=HTTP_200_OK)


class QuestionnaireViewSet(ModelViewSet):
    queryset = models.Questionnaire.objects.all()
    serializer_class = serializers.QuestionnaireSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.QuestionnaireLiteSerializer
        return serializers.QuestionnaireSerializer

    @action(methods=['get'], detail=False, url_name='my', url_path='my')
    def get_my_questionnaire(self, request, pk=None):
        profile = self.request.user.profile
        queryset = self.queryset.filter(creator=profile)
        if queryset.exists():
            return Response(data=serializers.QuestionnaireSerializer(queryset.first()).data, status=HTTP_200_OK)
        else:
            return Response(data=None, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='general-info', url_name='q_general_info')
    def general_info(self, request, pk=None):
        profile = self.request.user.profile
        data = {
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'middle_name': profile.middle_name,
            'email': profile.email,
            'number': profile.user.applicant.doc_num
        }
        return Response(data=data, status=HTTP_200_OK)


class FamilyMembershipViewSet(ModelViewSet):
    queryset = models.FamilyMembership.objects.all()
    serializer_class = serializers.FamilyMembershipSerializer
    permission_classes = (IsAdminOrReadOnly,)


class PrivilegeTypeViewSet(ModelViewSet):
    queryset = models.PrivilegeType.objects.all()
    serializer_class = serializers.PrivilegeTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class DocumentReturnMethodViewSet(ModelViewSet):
    queryset = models.DocumentReturnMethod.objects.all()
    serializer_class = serializers.DocumentReturnMethodSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecruitmentPlanViewSet(ModelViewSet):
    queryset = models.RecruitmentPlan.objects.all()
    serializer_class = serializers.RecruitmentPlanSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination

    @action(methods=['get'], detail=False, url_path='search', url_name='search_recruitment_plans')
    def search(self, request, pk=None):
        params = request.query_params
        user = self.request.user
        if user.profile.role.is_mod:
            lookup = Q()
        elif user.profile.role.is_applicant:
            lookup = Q(campaign=user.applicant.campaign) & Q(prep_level=user.applicant.prep_level)
        study_form = params.get('sf')
        if study_form:
            lookup = lookup & Q(study_form=study_form)
        language = params.get('lang')
        if language:
            lookup = lookup & Q(language=language)
        edu_program = params.get('ep')
        if edu_program:
            lookup = lookup & Q(education_program=edu_program)
        edu_program_group = params.get('epg')
        if edu_program_group:
            lookup = lookup & Q(education_program_group=edu_program_group)
        edu_base = params.get('eb')
        if edu_base:
            lookup = lookup & Q(admission_basis=edu_base)
        recruitment_plans = self.paginate_queryset(self.queryset.filter(lookup))
        if recruitment_plans:
            recruitment_plans = self.serializer_class(recruitment_plans, many=True).data
            return self.get_paginated_response(recruitment_plans)
        serializer = self.get_serializer(recruitment_plans, many=True)
        return Response(data={'results': serializer.data}, status=HTTP_200_OK)


class LanguageProficiencyViewSet(ModelViewSet):
    queryset = models.LanguageProficiency.objects.exclude(parent=None)
    serializer_class = serializers.LanguageProficiencySerializer
    permission_classes = (IsAdminOrReadOnly,)


class InternationalCertTypeViewSet(ModelViewSet):
    queryset = models.InternationalCertType.objects.all()
    serializer_class = serializers.InternationalCertTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class GrantTypeViewSet(ModelViewSet):
    queryset = models.GrantType.objects.all()
    serializer_class = serializers.GrantTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ApplicationStatusViewSet(ModelViewSet):
    queryset = models.ApplicationStatus.objects.all()
    serializer_class = serializers.ApplicationStatusSerializer


class ApplicationViewSet(ModelViewSet):
    queryset = models.Application.objects.annotate(cond_order=models.COND_ORDER).order_by('cond_order', '-created')
    serializer_class = serializers.ApplicationSerializer
    pagination_class = CustomPagination

    def check_done(self, profile):
        questionnaire = models.Questionnaire.objects.filter(creator=profile).exists()
        application = models.Application.objects.filter(creator=profile).exists()
        attachments = models.AdmissionDocument.objects.filter(creator=profile).exists()
        done = [
            questionnaire, application, attachments
        ]
        data = {
            'questionnaire': questionnaire,
            'application': application,
            'attachments': attachments,
            'done': all(done)
        }
        return data

    @action(methods=['get'], detail=False, url_path='done', url_name='legit')
    def is_done(self, request, pk=None):
        """Проверяет, что у абитуриента заполнены все 3 шага"""
        return Response(data={'data': self.check_done(self.request.user.profile)}, status=HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='submit', url_name='submit_to_moderator')
    def submit_to_moderator(self, request, pk=None):
        """Если все 3 шага заполнены, сменить статус на ожидает проверки. Тогда он появится у модератора."""
        profile = self.request.user.profile
        done = self.check_done(profile)['done']
        if done:
            application: models.Application = profile.application
            application.status = models.ApplicationStatus.objects.get(code=models.AWAITS_VERIFICATION)
            application.save()
            return Response(data={'ok': True}, status=HTTP_200_OK)
        else:
            raise ValidationError({'error': {'msg': 'all 3 steps not done'}})

    def retrieve(self, request, *args, **kwargs):
        application = self.get_object()
        profile = application.creator
        data = {
            'application': serializers.ApplicationSerializer(application).data
        }
        questionnaire = models.Questionnaire.objects.filter(creator=profile)
        if questionnaire.exists():
            data['questionnaire'] = serializers.QuestionnaireSerializer(questionnaire.first()).data
        else:
            data['questionnaire'] = None
        attachments = models.AdmissionDocument.objects.filter(creator=profile)
        if attachments.exists():
            data['attachments'] = serializers.AdmissionDocumentSerializer(attachments, many=True).data
        else:
            data['attachments'] = None
        return Response(data=data, status=HTTP_200_OK)

    def validate(self, validated_data, user):
        campaign: models.AdmissionCampaign = user.applicant.campaign
        directions = validated_data.get('directions')
        if campaign.chosen_directions_max_count < len(directions):
            raise ValidationError({"error": {
                "msg": "max_selected_directions"
            }})
        is_grant_holder = validated_data.get('is_grant_holder')
        if is_grant_holder:
            grant = validated_data.get('grant', None)
            grant_epg = models.EducationProgramGroup.objects.get(pk=grant.get('edu_program_group'))
            # Если грантник, то первое направление должно соответствовать группе обр. программ в гранте,
            # бюджетному основанию поступления и очной форме обучения
            first_direction = models.RecruitmentPlan.objects.get(
                pk=list(filter(lambda direction: direction['order_number'] == 0, directions))[0]['plan']
            )
            budget_admission_basis = models.EducationBase.objects.get(code='budget')
            full_time_study_form = models.StudyForm.objects.get(code='full-time')
            if (first_direction.education_program_group != grant_epg) or (
                    first_direction.admission_basis != budget_admission_basis) or (
                    first_direction.study_form != full_time_study_form):
                raise ValidationError({'error': {
                    "msg": "direction_and_grant_no_match"
                }})
        international_certs = validated_data.get('international_certs', None)
        if international_certs and not campaign.inter_cert_foreign_lang:
            validated_data['international_certs'] = None
        unpassed_test = validated_data.get('unpassed_test', False)
        if unpassed_test:
            validated_data.pop('test_result', None)

    def create(self, request, *args, **kwargs):
        self.validate(request.data, self.request.user)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.validate(request.data, self.request.user)
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ApplicationLiteSerializer
        return serializers.ApplicationSerializer

    @action(methods=['get'], detail=False, url_name='my', url_path='my')
    def get_my_application(self, request, pk=None):
        profile: Profile = self.request.user.profile
        queryset = self.queryset.filter(creator=profile)
        if queryset.exists():
            return Response(data=serializers.ApplicationLiteSerializer(queryset.first()).data, status=HTTP_200_OK)
        else:
            return Response(data=None, status=HTTP_200_OK)


    @action(methods=['post'], detail=True, url_path='apply-action', url_name='apply_action')
    def apply_action(self, request, pk=None):
        """Применение действий модераоторм
        вместо того чтобы делать несколько эндпоинтов, создан один, который будет применять
        тип действия от модератора.
        action_type - тип действия
        comment - требуется в некоторых действиях

        approve - заявление подтверждается, абитуриент становится студентом

        reject - заявление отклоняется, абитуриент должен быть удален к
        завершению приемной кампании и должен ждать следующий год, чтобы по новой подать документы
        """
        profile: Profile = self.request.user.profile
        application = self.get_object()
        if models.Application.can_perform_action(profile=profile):
            action_type: str = request.data.get('action')
            comment = request.data.get('comment')
            # Одобряем заявление
            if action_type == 'approve':
                application.approve(moderator=profile, comment=comment)
            # Отклоняем (осуждаем) заявление
            elif action_type == 'reject':
                if not comment:
                    raise ValidationError({'error': 'comment is required'})
                application.reject(moderator=profile, comment=comment)
            elif action_type == 'improve':
                if not comment:
                    raise ValidationError({'error': 'comment is required'})
                application.improve(moderator=profile, comment=comment)
            # Отпаравляем заявление на доработку - не заполнил анкету или неправильно заполлнил заявление
            return Response(data={'message': f'successfully applied action: {action_type}'})
        else:
            raise ValidationError({'error': f'profile is moderator? {profile.role.is_mod}'})

    @action(methods=['get'], detail=False, url_path='search', url_name='application_search')
    def search(self, request, pk=None):
        """Фильтр по заявлениям
        Параметры:
        ap: uid - applicant profile - профиль абитуриента
        pl: uid - preparation level - уровень подготовки
        epg: uid - education program group - группа образовательных программ
        ad: str(date) - apply date - дата подачи заявления
        """
        query_params = request.query_params
        applicant_profile: str = query_params.get('ap', None)
        prep_level: str = query_params.get('pl', None)
        edu_program_group: str = query_params.get('epg', None)
        apply_date: str = query_params.get('ad', None)
        lookup = Q()
        if applicant_profile:
            lookup = lookup | Q(creator__uid=applicant_profile)
        if prep_level:
            lookup = lookup | Q(creator__user__applicant__prep_level=prep_level)
        if edu_program_group:
            lookup = lookup | Q(directions__education_program_group=edu_program_group)
        if apply_date:
            if '.' in apply_date:
                apply_date = '-'.join(apply_date.split('.')[::-1])
            lookup = lookup | Q(created=apply_date)
        queryset = self.queryset.filter(lookup).distinct()
        paginated_queryset = self.paginate_queryset(queryset=queryset)
        return self.get_paginated_response(serializers.ApplicationLiteSerializer(paginated_queryset, many=True).data)

    @action(methods=['get'], detail=False, url_path='current-campaign', url_name='current_campaign')
    def get_current_campaign(self, request, pk=None):
        campaign = self.request.user.applicant.campaign
        return Response(data=campaign.info, status=HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='save-directions', url_name='save_directions')
    def save_directions(self, request, pk=None):
        """Сохранение направлений
        Доступно только модераторам.
        Удалить все предыдущие направелния, подставить новые, уведомить абитуриента
        """
        profile = self.request.user.profile
        role = profile.role
        if role.is_mod:
            application: models.Application = self.get_object()
            directions = request.data.pop('directions')
            directions_set_by_moderator = []
            for direction in directions:
                directions_set_by_moderator.append(models.OrderedDirection.objects.create(
                    plan=models.RecruitmentPlan.objects.get(pk=direction['plan']),
                    order_number=direction['order_number']
                ))
            application.directions.all().delete()
            application.directions.add(*directions_set_by_moderator)
            application.save()
            # Почта может не работать, как у меня на локали
            try:
                send_mail(
                    subject='Изменение направлений',
                    message=f'Ваши выбранные направления были изменены модератором {profile.full_name}',
                    from_email='',
                    recipient_list=[application.creator.email])
            except Exception as e:
                # Положить в очередь крона
                print(e)
            return Response(data=None, status=HTTP_200_OK)
        else:
            raise ValidationError({"error": "access_denied"})

    @action(methods=['get'], detail=False, url_path='my_status', url_name='my_status')
    def get_my_status(self, request, pk=None):
        profile = self.request.user.profile
        queryset = models.Application.objects.filter(creator=profile).first()
        if queryset is not None:
            data = serializers.ApplicantMyStatusSerializer(queryset).data
            return Response(data=data, status=HTTP_200_OK)
        else:
            data = {
                "status": "Составьте заявление",
                "comment": "",
            }
            return Response(data=data, status=HTTP_200_OK)


class AdmissionCampaignTypeViewSet(ModelViewSet):
    queryset = models.AdmissionCampaignType.objects.all()
    serializer_class = serializers.AdmissionCampaignTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AdmissionCampaignViewSet(ModelViewSet):
    queryset = models.AdmissionCampaign.objects.all()
    serializer_class = serializers.AdmissionCampaignSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @action(methods=['get'], detail=False, url_path='open', url_name='open_campaigns')
    def get_open_campaigns(self, request, pk=None):
        today = dt.date.today()
        campaigns = self.queryset.filter(
            Q(start_date__lte=today)
            & Q(end_date__gte=today)
            & Q(is_active=True)
            & Q(year=today.year)
        )
        logger.info('campaigns')
        return Response({'open': campaigns.exists()}, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='open-prep-levels', url_name='open_prep_levels')
    def get_open_prep_levels(self, request, pk=None):
        prep_levels = models.PreparationLevel.objects.filter(
            pk__in=self.queryset.values_list('type__prep_levels')).distinct()
        prep_levels = list(map(lambda x: {'uid': x.uid, 'name': x.name}, prep_levels))
        return Response(data=prep_levels, status=HTTP_200_OK)


class AddressViewSet(ModelViewSet):
    queryset = models.Address.objects.all()
    serializer_class = serializers.AddressSerializer

    @action(methods=['get'], detail=False, url_path='regions', url_name='get_regions')
    def get_regions(self, request, pk=None):
        regions = models.AddressClassifier.objects.filter(address_element_type=1)
        data = serializers.AddressClassifierSerializer(regions, many=True).data
        return Response(data=data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='districts', url_name='districts')
    def get_districts(self, request, pk=None):
        region = models.AddressClassifier.objects.filter(pk=request.query_params.get('region')).first()
        districts = models.AddressClassifier.objects.filter(address_element_type=2, region_code=region.region_code)
        data = serializers.AddressClassifierSerializer(districts, many=True).data
        return Response(data=data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='cities', url_name='cities')
    def get_cities(self, request, pk=None):
        district = models.AddressClassifier.objects.filter(pk=request.query_params.get('district')).first()
        cities = models.AddressClassifier.objects.filter(address_element_type=3, region_code=district.region_code)
        data = serializers.AddressClassifierSerializer(cities, many=True).data
        return Response(data=data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='localities', url_name='localities')
    def get_localities(self, request, pk=None):
        district = models.AddressClassifier.objects.filter(pk=request.query_params.get('district')).first()
        localities = models.AddressClassifier.objects.filter(
            address_element_type=4,
            region_code=district.region_code,
            district_code=district.district_code,
        )
        data = serializers.AddressClassifierSerializer(localities, many=True).data
        return Response(data=data, status=HTTP_200_OK)


class AdmissionDocumentViewSet(ModelViewSet):
    queryset = models.AdmissionDocument.objects.all()
    serializer_class = serializers.AdmissionDocumentSerializer

    def create(self, request, *args, **kwargs):
        request.data['creator'] = self.request.user.profile.pk
        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_name='my', url_path='my')
    def get_my_attachments(self, request, pk=None):
        profile: Profile = self.request.user.profile
        queryset = self.queryset.filter(creator=profile)
        if queryset.exists():
            serializer = serializers.AdmissionDocumentSerializer(queryset, many=True)
            return Response(data=serializer.data, status=HTTP_200_OK)
        else:
            return Response(data=None, status=HTTP_200_OK)

    @action(methods=['post'], detail=False, url_name='multiple-create', url_path='multiple-create')
    def multiple_create(self, request, pk=None):
        try:
            creator = self.request.user.profile
            documents = request.data.get('documents')
            creator.admissiondocument_set.all().delete()
            for document in documents:
                print(document)
                models.AdmissionDocument.objects.create(
                    document_1c=models.Document1C.objects.get(pk=document['doc1c']),
                    document=models.Document.objects.get(pk=document['document']),
                    creator=creator
                )
            return Response(data={"msg": "created"}, status=HTTP_200_OK)
        except Exception as e:
            raise ValidationError({"error": {"msg": "something went wrong", "exc": e}})


class ModeratorViewSet(ModelViewSet):
    queryset = models.Application.objects.all()
    serializer_class = serializers.ModeratorSerializer
    pagination_class = CustomPagination

    def list(self, request):
        queryset = self.queryset
        application_status = request.query_params.get('status')
        full_name = request.query_params.get('full_name')
        preparation_level = request.query_params.get('preparation_level')
        edu_program_groups = request.query_params.get('edu_program_groups')
        application_date = request.query_params.get('application_date')
        without_applications = request.query_params.get('without_applications')

        if without_applications:
            questionnaire_query = models.Questionnaire.objects.filter(creator__application=None)
            questionnaire_serializer = serializers.ModeratorQuestionnaireSerializer
            page = self.paginate_queryset(questionnaire_query)
            serializer = questionnaire_serializer(page, many=True).data
            paginated_response = self.get_paginated_response(serializer)
            return Response(data=paginated_response.data, status=HTTP_200_OK)



        if application_status is not None:
            if application_status == models.NO_QUESTIONNAIRE:
                queryset = queryset.filter(status=None)
            else:
                queryset = queryset.filter(status__code=application_status)


        if full_name is not None:
            lookup = Q(creator__first_name__contains=full_name) \
                     | Q(creator__last_name__contains=full_name) \
                     | Q(creator__middle_name__contains=full_name)
            queryset = queryset.filter(lookup)
        if preparation_level is not None:
            queryset = queryset.filter(directions__plan__preparaion_level=preparation_level)
        if edu_program_groups is not None:
            queryset = queryset.filter(directions__plan__education_program_group=edu_program_groups)
        if application_date is not None:
            queryset = queryset.filter(created=application_date)

        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True).data
        paginated_response = self.get_paginated_response(serializer)
        return Response(data=paginated_response.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='statuses', url_name='statuses')
    def get_statuses(self, request, pk=None):
        statuses = models.ApplicationStatus.objects.all()
        data = serializers.ApplicationStatusSerializer(statuses, many=True).data
        return Response(data=data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_name='get_application', url_path='get_application')
    def get_application(self, request, pk=None):
        application_uid = request.query_params.get('uid')
        queryset = self.queryset.filter(pk=application_uid)
        return Response(data=serializers.ApplicationSerializer(queryset.first()).data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='get_questionnaire', url_name='get_questionnaire')
    def get_questionnaire(self, request, pk=None):
        application_uid = self.request.query_params.get('uid')
        queryset = self.queryset.get(pk=application_uid)
        questionnaire = models.Questionnaire.objects.filter(creator=queryset.creator)
        if questionnaire.exists():
            return Response(data=serializers.QuestionnaireSerializer(questionnaire.first()).data, status=HTTP_200_OK)
        else:
            return Response(data=None, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='get_application_status_history',
            url_name='get_application_status_history')
    def get_history(self, request, pk=None):
        application_uid = self.request.query_params.get('uid')
        queryset = self.queryset.get(pk=application_uid)
        history = models.ApplicationStatusChangeHistory.objects.filter(author=queryset.creator)
        if history.exists():
            return Response(data=serializers.ApplicationChangeHistorySerializer(history, many=True).data,
                            status=HTTP_200_OK)
        else:
            return Response(data=None, status=HTTP_200_OK)


class Document1CViewSet(ModelViewSet):
    queryset = models.Document1C.objects.order_by('name_ru', 'name_kk', 'name_en').all()
    serializer_class = serializers.Document1CSerializer

    @action(methods=['get'], detail=False, url_path='campaign-docs', url_name='campaign-docs')
    def get_current_applicant_campaign_documents(self, request, pk=None):
        """
        Получить документы приемной кампании текущего абитуриента
        """
        try:
            campaign = self.request.user.applicant.campaign
            serializer = serializers.Document1CSerializer(campaign.documents.all(), many=True)
            return Response(data=serializer.data, status=HTTP_200_OK)
        except Exception as e:
            raise ValidationError({"error": {"msg": "something went wrong", "exc": e}})
