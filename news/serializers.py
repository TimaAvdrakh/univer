from rest_framework.serializers import ModelSerializer
from .models import News


class NewsSerializer(ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

    def create(self, validated_data):
        instance = super().create(validated_data)
        # По фильтру с фронта вытащить ключи и по значениям вывести критерии 
        request = self.context['request'].data
        return instance
