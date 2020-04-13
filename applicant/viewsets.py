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
from .models import (
    Applicant,
    Questionnaire,
    FamilyMembership,
    PrivilegeType,
    DocumentReturnMethod,
    AddressType,
    DocScan,
    RecruitmentPlan,
    LanguageProficiency,
    InternationalCertType,
    GrantType,
    Application,
    ApplicationStatus,
    AdmissionCampaign,
    AdmissionCampaignType,
    COND_ORDER
)
from .serializers import (
    ApplicantSerializer,
    ApplicationLiteSerializer,
    QuestionnaireSerializer,
    FamilyMembershipSerializer,
    PrivilegeTypeSerializer,
    DocumentReturnMethodSerializer,
    AddressTypeSerializer,
    RecruitmentPlanSerializer,
    LanguageProficiencySerializer,
    InternationalCertTypeSerializer,
    GrantTypeSerializer,
    ApplicationSerializer,
    ApplicationStatusSerializer,
    AdmissionCampaignTypeSerializer,
    AdmissionCampaignSerializer,
)
from .token import token_generator


# Спец форма для того, чтобы парсить файлы
class DocScanForm(forms.ModelForm):
    class Meta:
        model = DocScan
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
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    @action(methods=['post'], detail=False, url_path='campaign-types', url_name='campaign_types')
    def get_campaign_types(self, request, pk=None):
        prep_level = request.data.get('prep_level')
        campaign_types = AdmissionCampaignType.objects.filter(prep_levels=prep_level)
        return Response(data=AdmissionCampaignTypeSerializer(campaign_types, many=True).data, status=HTTP_200_OK)

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
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer

    @action(methods=['get'], detail=False, url_name='my', url_path='my')
    def get_my_questionnaire(self, request, pk=None):
        profile = self.request.user.profile
        queryset = self.queryset.filter(creator=profile)
        if queryset.exists():
            return Response(data=QuestionnaireSerializer(queryset.first()).data, status=HTTP_200_OK)
        else:
            return Response(data={"uid": None}, status=HTTP_200_OK)


class FamilyMembershipViewSet(ModelViewSet):
    queryset = FamilyMembership.objects.all()
    serializer_class = FamilyMembershipSerializer
    permission_classes = (IsAdminOrReadOnly,)


class PrivilegeTypeViewSet(ModelViewSet):
    queryset = PrivilegeType.objects.all()
    serializer_class = PrivilegeTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class DocumentReturnMethodViewSet(ModelViewSet):
    queryset = DocumentReturnMethod.objects.all()
    serializer_class = DocumentReturnMethodSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AddressTypeViewSet(ModelViewSet):
    queryset = AddressType.objects.all()
    serializer_class = AddressTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecruitmentPlanViewSet(ModelViewSet):
    queryset = RecruitmentPlan.objects.all()
    serializer_class = RecruitmentPlanSerializer
    permission_classes = (IsAdminOrReadOnly,)


class LanguageProficiencyViewSet(ModelViewSet):
    queryset = LanguageProficiency.objects.exclude(parent=None)
    serializer_class = LanguageProficiencySerializer
    permission_classes = (IsAdminOrReadOnly,)


class InternationalCertTypeViewSet(ModelViewSet):
    queryset = InternationalCertType.objects.all()
    serializer_class = InternationalCertTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class GrantTypeViewSet(ModelViewSet):
    queryset = GrantType.objects.all()
    serializer_class = GrantTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ApplicationStatusViewSet(ModelViewSet):
    queryset = ApplicationStatus.objects.all()
    serializer_class = ApplicationStatusSerializer


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.annotate(cond_order=COND_ORDER).order_by('cond_order')
    serializer_class = ApplicationSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return ApplicationLiteSerializer
        else:
            return ApplicationSerializer

    @action(methods=['get'], detail=False, url_name='my', url_path='my')
    def get_my_application(self, request, pk=None):
        profile: Profile = self.request.user.profile
        queryset = self.queryset.filter(creator=profile)
        if queryset.exists():
            return Response(data=ApplicationLiteSerializer(queryset.first()).data, status=HTTP_200_OK)
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
        application: Application = self.get_object()
        if Application.can_perform_action(profile=profile):
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
        queryset = self.queryset.filter(lookup).distinct()
        paginated_queryset = self.paginate_queryset(queryset=queryset)
        return self.get_paginated_response(ApplicationLiteSerializer(paginated_queryset, many=True).data)


class AdmissionCampaignTypeViewSet(ModelViewSet):
    queryset = AdmissionCampaignType.objects.all()
    serializer_class = AdmissionCampaignTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AdmissionCampaignViewSet(ModelViewSet):
    queryset = AdmissionCampaign.objects.all()
    serializer_class = AdmissionCampaignSerializer
    permission_classes = (IsAdminOrReadOnly,)
