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
            'count_credits',
        )
