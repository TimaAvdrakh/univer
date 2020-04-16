from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Q
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
from .token import token_generator


# Спец форма для того, чтобы парсить файлы
class DocScanForm(forms.ModelForm):
    class Meta:
        model = models.DocScan
        fields = "__all__"


# Запись в media
def handle_uploaded_file(f):
    media_catalog = settings.MEDIA_ROOT
    filename = f.name
    with open(f"{media_catalog}/{filename}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def file_upload(request):
    # TODO add path
    if request.method == "POST":
        if request.FILES:
            # Сюда пишем id-шники DocScan, чтобы потом связать с заявкой
            doc_scan_ids = []
            if len(request.FILES) > 1:
                for item in request.FILES.get("files"):
                    # Может привести к багу если несколько файлов
                    form = DocScanForm(request.POST, item)
                    if form.is_valid():
                        form.instance.name = item.name
                        form.instance.ext = item.name.split(".")[-1]
                        form.instance.size = item.size
                        form.instance.content_type = item.content_type
                        form.instance.path = f"{settings.MEDIA_ROOT}/{item.name}"
                        form.save(commit=True)
                        doc_scan_ids.append(form.instance.id)
                        handle_uploaded_file(item)
                    else:
                        raise Exception("An error occurred")
            else:
                form = DocScanForm(request.POST, request.FILES)
                if form.is_valid():
                    file = request.FILES.get("file")
                    form.instance.name = file.name
                    form.instance.ext = file.name.split(".")[-1]
                    form.instance.size = file.size
                    form.instance.content_type = file.content_type
                    form.instance.path = f"{settings.MEDIA_ROOT}/{file.name}"
                    form.save(commit=True)
                    handle_uploaded_file(file)
                    doc_scan_ids.append(form.instance.id)
            return JsonResponse({"ids": doc_scan_ids})
        else:
            return HttpResponseBadRequest(
                content_type=b"application/pdf", content="Send files"
            )
    else:
        return HttpResponse(content_type=b"text/html", content="Method GET not allowed")


# Активация аккаунта
def activate(request, uidb64, token):
    user = None
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        HttpResponseBadRequest(e)
    if user and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse("Account activated")
    else:
        return HttpResponseBadRequest("No user")


class ApplicantViewSet(ModelViewSet):
    queryset = models.Applicant.objects.all()
    serializer_class = serializers.ApplicantSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

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

    @action(methods=['get'], detail=False, url_name='my', url_path='my')
    def get_my_questionnaire(self, request, pk=None):
        profile = self.request.user.profile
        queryset = self.queryset.filter(creator=profile)
        if queryset.exists():
            return Response(data=serializers.QuestionnaireSerializer(queryset.first()).data, status=HTTP_200_OK)
        else:
            return Response(data={"uid": None}, status=HTTP_200_OK)


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


class AddressTypeViewSet(ModelViewSet):
    queryset = models.AddressType.objects.all()
    serializer_class = serializers.AddressTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecruitmentPlanViewSet(ModelViewSet):
    queryset = models.RecruitmentPlan.objects.all()
    serializer_class = serializers.RecruitmentPlanSerializer
    permission_classes = (IsAdminOrReadOnly,)


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
    queryset = models.Application.objects.annotate(cond_order=models.COND_ORDER).order_by('cond_order')
    serializer_class = serializers.ApplicationSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ApplicationLiteSerializer
        else:
            return serializers.ApplicationSerializer

    @action(methods=['get'], detail=False, url_name='my', url_path='my')
    def get_my_application(self, request, pk=None):
        profile: Profile = self.request.user.profile
        queryset = self.queryset.filter(creator=profile)
        if queryset.exists():
            return Response(data=serializers.ApplicationLiteSerializer(queryset.first()).data, status=HTTP_200_OK)
        else:
            return Response(data={"uid": None}, status=HTTP_200_OK)

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

        improve - заявление отправляется на доработку, только в том случае если заявление валидно, но допущены
        какие-то ошибки - опечатки, не та информация
        """
        profile: Profile = self.request.user.profile
        application = self.get_object()
        if models.Application.can_perform_action(profile=profile):
            action_type: str = request.get('action')
            comment = request.get('comment')
            # Одобряем заявление
            if action_type == 'approve':
                application.approve(moderator=profile, comment=comment)
            # Отклоняем (осуждаем) заявление
            elif action_type == 'reject':
                if not comment:
                    raise ValidationError({'error': 'comment is required'})
                application.reject(moderator=profile, comment=comment)
            # Отпаравляем заявление на доработку - не заполнил анкету или неправильно заполлнил заявление
            elif action_type == 'improve':
                if not comment:
                    raise ValidationError({'error': 'comment is required'})
                application.improve(moderator=profile, comment=comment)
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
        queryset = models.self.queryset.filter(lookup).distinct()
        paginated_queryset = models.self.paginate_queryset(queryset=queryset)
        return self.get_paginated_response(serializers.ApplicationLiteSerializer(paginated_queryset, many=True).data)

    @action(methods=['get'], detail=False, url_path='current-campaign', url_name='current_campaign')
    def get_current_campaign(self, request, pk=None):
        campaign = self.request.user.applicant.campaign
        return Response(data={
            # cdmc - максимум направлений, которые может выбрать абитуриент в этой кампании
            'cdmc': campaign.chosen_directions_max_count,
            # icfl - кампания принимает международные сертификаты
            'icfl': campaign.inter_cert_foreign_lang
        }, status=HTTP_200_OK)


class AdmissionCampaignTypeViewSet(ModelViewSet):
    queryset = models.AdmissionCampaignType.objects.all()
    serializer_class = serializers.AdmissionCampaignTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AdmissionCampaignViewSet(ModelViewSet):
    queryset = models.AdmissionCampaign.objects.all()
    serializer_class = serializers.AdmissionCampaignSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AddressViewSet(ModelViewSet):
    queryset = models.Address.objects.all()
    serializer_class = serializers.AddressSerializer

    @action(methods=['get'], detail=False, url_path='search', url_name='address_search')
    def search(self, request, pk=None):
        name, code = request.query_params.get('name'), request.query_params.get('code')
        if not name:
            raise ValidationError({"error": "pass name"})
        addresses = models.Address.get_by(name=name, code=code)
        data = serializers.AddressSerializer(addresses, many=True).data
        return Response(data=data, status=HTTP_200_OK)
