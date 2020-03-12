from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import *


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


# dbg
# отдельный ендпоинт для выгрузки файла
@csrf_exempt
def file_upload(request):
    # TODO add path
    if request.method == "POST":
        if request.FILES:
            # Сюда пишем id-шники DocScan, чтобы потом связать с заявкой
            doc_scan_ids = []
            if len(request.FILES) > 1:
                for item in request.FILES.get("file"):
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
                content_type=b"application/pdf", content="Отправьте файлы"
            )


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
    permission_classes = (permissions.AllowAny,)


class QuestionnaireViewSet(ModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permissions = (permissions.AllowAny,)


class AdmissionApplicationViewSet(ModelViewSet):
    queryset = AdmissionApplication.objects.all()
    serializer_class = AdmissionApplicationSerializer


class ApplicantLogin(APIView):
    pass
