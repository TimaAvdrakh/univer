from rest_framework import serializers
from organizations import models as org_models


class AcadPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.AcadPeriod
        fields = (
            'uid',
            'name',
        )

