from rest_framework import serializers
from organizations import models as org_models
from . import models
from portal_users.models import Level, AchievementType


class FilteredListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(is_active=True)
        return super().to_representation(data)


class AcadPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.AcadPeriod
        fields = (
            'uid',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['name'] = instance.repr_name

        return data


class RegistrationPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RegistrationPeriod
        fields = (
            'uid',
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


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = (
            'uid',
            'name',
        )


class AchievementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AchievementType
        fields = (
            'uid',
            'name',
        )


class IdentityDocumentSerializer(serializers.ModelSerializer):
    document_type = serializers.CharField()
    issued_by = serializers.CharField()

    class Meta:
        model = models.IdentityDocument
        fields = (
            'document_type',
            'serial_number',
            'number',
            'given_date',
            'validity_date',
            'issued_by',
        )


class EducationSerializer(serializers.ModelSerializer):
    document_type = serializers.CharField()
    edu_type = serializers.CharField()
    institute = serializers.CharField()

    class Meta:
        model = org_models.Education
        fields = (
            'document_type',
            'edu_type',
            'serial_number',
            'number',
            'given_date',
            'institute',
        )


class StudyPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.StudyPeriod
        fields = (
            'uid',
            'start',
            'end',
        )


class StudyFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.StudyForm
        fields = (
            'uid',
            'name',
        )


class CourseSerializer(serializers.ModelSerializer):
    uid = serializers.IntegerField(
        source='number',
    )

    class Meta:
        model = models.Course
        fields = (
            'uid',
            'name',
        )


class StudentDisciplineStatusSerializer(serializers.ModelSerializer):
    uid = serializers.IntegerField(
        source='number',
    )

    class Meta:
        model = org_models.StudentDisciplineStatus
        fields = (
            'name',
            'uid',
        )
