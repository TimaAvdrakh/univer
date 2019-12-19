from rest_framework import serializers
from schedules import models as sh_models


class AllowMarkLessonSerializer(serializers.ModelSerializer):
    """Разрешить оценивать выбранное занятие,"""
    class Meta:
        model = sh_models.Lesson
        fields = (
            'uid',
            'admin_allow',
        )

    def update(self, instance, validated_data):
        instance.admin_allow = not instance.admin_allow
        instance.save()

        return instance


# class LessonListView(serializers.ModelSerializer):
