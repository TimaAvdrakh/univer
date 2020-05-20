from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from common.paginators import CustomPagination
from univer_admin.permissions import IsAdminOrReadOnly
from .models import *
from .serializers import *


class PreparationLevelViewSet(ModelViewSet):
    queryset = PreparationLevel.objects.all()
    serializer_class = PreparationLevelSerializer
    permission_classes = (IsAdminOrReadOnly,)


class StudyFormViewSet(ModelViewSet):
    queryset = StudyForm.objects.all()
    serializer_class = StudyFormSerializer
    permission_classes = (IsAdminOrReadOnly,)


class EducationTypeViewSet(ModelViewSet):
    queryset = EducationType.objects.all()
    serializer_class = EducationTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class EducationBaseViewSet(ModelViewSet):
    queryset = EducationBase.objects.all().order_by('name_ru', 'name_en', 'name_kk').distinct('name_ru', 'name_en', 'name_kk')
    serializer_class = EducationBaseSerializer
    permission_classes = (IsAdminOrReadOnly,)


class EducationProgramViewSet(ModelViewSet):
    queryset = EducationProgram.objects.all().order_by('name_ru', 'name_en', 'name_kk').distinct('name_ru', 'name_en', 'name_kk')
    serializer_class = EducationProgramSerializer
    permission_classes = (IsAdminOrReadOnly,)


class EducationProgramGroupViewSet(ModelViewSet):
    queryset = EducationProgramGroup.objects.all().order_by('name_ru', 'name_en', 'name_kk').distinct('name_ru', 'name_en', 'name_kk')
    serializer_class = EducationProgramGroupSerializer
    permission_classes = (IsAdminOrReadOnly,)


class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all().order_by('name_ru', 'name_en', 'name_kk').distinct('name_ru', 'name_en', 'name_kk')
    serializer_class = OrganizationSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination

    @action(methods=['get'], detail=False, url_path='search', url_name='search_organizations')
    def search(self, request, pk=None):
        name = request.query_params.get('name')
        data = self.queryset.filter(
            Q(name_ru__icontains=name)
            | Q(name_en__icontains=name)
            | Q(name_kk__icontains=name)
        ).distinct()[:20]
        data = self.serializer_class(data, many=True).data
        return Response(data=data)


class SpecialityViewSet(ModelViewSet):
    queryset = Speciality.objects.all().order_by('name_ru', 'name_en', 'name_kk').distinct('name_ru', 'name_en', 'name_kk')
    serializer_class = SpecialitySerializer
    permission_classes = (IsAdminOrReadOnly,)


class LanguageViewSet(ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = (IsAdminOrReadOnly,)


class DisciplineViewSet(ModelViewSet):
    queryset = Discipline.objects.all().order_by('name_ru', 'name_en', 'name_kk').distinct('name_ru', 'name_en', 'name_kk')
    serializer_class = DisciplineSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination

    @action(methods=['get'], detail=False, url_path='search', url_name='search_disciplines')
    def search(self, request, pk=None):
        name = request.query_params.get('name')
        data = self.queryset.filter(
            Q(name_ru__icontains=name)
            | Q(name_en__icontains=name)
            | Q(name_kk__icontains=name)
        ).distinct()[:20]
        data = self.serializer_class(data, many=True).data
        return Response(data=data)

