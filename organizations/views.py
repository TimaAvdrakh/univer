from rest_framework.viewsets import ModelViewSet
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
