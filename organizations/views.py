from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
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


class EducationModelViewSet(ModelViewSet):
    queryset = EducationBase.objects.all()
    serializer_class = EducationBaseSerializer
    permission_classes = (IsAdminOrReadOnly,)


class EducationProgramViewSet(ModelViewSet):
    queryset = EducationProgram.objects.all()
    serializer_class = EducationProgramSerializer
    permission_classes = (IsAdminOrReadOnly,)


class EducationProgramGroupViewSet(ModelViewSet):
    queryset = EducationProgramGroup.objects.all()
    serializer_class = EducationProgramGroupSerializer
    permission_classes = (IsAdminOrReadOnly,)


class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @action(methods=['get'], detail=False, url_path='search', url_name='search')
    def search(self, request, pk=None):
        search = request.query_params.get('name')
        organizations = self.queryset.filter(
            Q(name_ru__icontains=search) |
            Q(name_kk__icontains=search) |
            Q(name_en__icontains=search)
        ).distinct()[:20]
        return Response(self.serializer_class(organizations, many=True).data)


class SpecialityViewSet(ModelViewSet):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = (IsAdminOrReadOnly,)


class LanguageViewSet(ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = (IsAdminOrReadOnly,)


class DisciplineViewSet(ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @action(methods=['get'], detail=False, url_path='search', url_name='search')
    def search(self, request, pk=None):
        search = request.query_params.get('name')
        disciplines = self.queryset.filter(
            Q(name_ru__icontains=search) |
            Q(name_kk__icontains=search) |
            Q(name_en__icontains=search)
        ).distinct()[:20]
        return Response(self.serializer_class(disciplines, many=True).data)
