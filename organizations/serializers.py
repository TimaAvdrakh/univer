from rest_framework import serializers
from . import models


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = (
            "uid",
            "name",
        )


class PreparationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PreparationLevel
        fields = "__all__"


class StudyFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudyForm
        fields = "__all__"


class DisciplineSerializer2(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = (
            'uid',
            'name',
        )


class EducationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EducationType
        fields = '__all__'


class EducationBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EducationBase
        fields = '__all__'


class EducationProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EducationProgram
        fields = '__all__'


class EducationProgramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EducationProgramGroup
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = '__all__'


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Speciality
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language
        fields = '__all__'
