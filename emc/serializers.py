from rest_framework import serializers
from .models import EMC


class EMCSerializer(serializers.ModelSerializer):
    discipline = serializers.SlugRelatedField(slug_field='name', read_only=True)
    language = serializers.SlugRelatedField(slug_field='name', read_only=True)
    files = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = EMC
        fields = ('discipline', 'language', 'files', 'author', 'description')


class EMCCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMC
        fields = ('discipline', 'language', 'files', 'description')
