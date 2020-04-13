from rest_framework import serializers
from . import models
from common.exceptions import CustomException


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Type
        fields = (
            'uid',
            'name',
        )