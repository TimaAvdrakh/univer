from rest_framework import serializers
from . import models


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = (
            'uid',
            'name',
        )

