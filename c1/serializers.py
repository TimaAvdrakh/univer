from rest_framework import serializers
from . import models
from common.exceptions import CustomException
from datetime import datetime
from schedules import models as sh_models
from portal_users import models as user_models


class C1ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.C1Object
        fields = (
            'uid',
            'name',
            'model',
            'is_related',
        )


class C1ObjectCompareSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.C1ObjectCompare
        fields = (
            'uid',
            'name',
            'c1_object',
            'c1',
            'django',
            'main_field',
            'is_binary_data',
        )
