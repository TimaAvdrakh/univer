from rest_framework import serializers
from .models import EMC


class EMCSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMC
        fields = ('discipline', 'language', 'files', 'author', 'description')
