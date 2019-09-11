from rest_framework import serializers
from organizations import models as org_models
from . import models


class AcadPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.AcadPeriod
        fields = (
            'uid',
            'name',
        )


class RegistrationPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RegistrationPeriod
        fields = (
            'name',
            'start_date',
            'end_date',
        )


class CourseAcadPeriodPermissionSerializer(serializers.ModelSerializer):
    acad_period = AcadPeriodSerializer()
    registration_period = RegistrationPeriodSerializer()

    class Meta:
        model = models.CourseAcadPeriodPermission
        fields = (
            'registration_period',
            'acad_period',
        )



