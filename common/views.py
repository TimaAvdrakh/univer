from rest_framework import generics
from . import serializers
from organizations import models as org_models


class AcadPeriodList(generics.ListAPIView):
    """Получить список академического период"""
    queryset = org_models.AcadPeriod.objects.filter(is_active=True)
    serializer_class = serializers.AcadPeriodSerializer
