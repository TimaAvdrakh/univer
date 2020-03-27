from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *


class PreparationLevelViewSet(viewsets.ModelViewSet):
    queryset = PreparationLevel.objects.all()
    serializer_class = PreparationLevelSerializer
    permission_classes = (AllowAny,)


class StudyFormViewSet(viewsets.ModelViewSet):
    queryset = StudyForm.objects.all()
    serializer_class = StudyFormSerializer
    permission_classes = (AllowAny,)
