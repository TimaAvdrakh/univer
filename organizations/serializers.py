from rest_framework import serializers
from . import models


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = ("uid", "name",)


class PreparationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PreparationLevel
        fields = ['uid', 'name']


class StudyFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudyForm
        fields = ['uid', 'name']


class EducationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EducationType
        fields = ['uid', 'name']


class EducationBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EducationBase
        fields = ['uid', 'name']


class EducationProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EducationProgram
        fields = ['uid', 'name']


class EducationProgramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EducationProgramGroup
        fields = ['uid', 'name']


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = ['uid', 'name']


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Speciality
        fields = ['uid', 'name']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language
        fields = ['uid', 'name']
