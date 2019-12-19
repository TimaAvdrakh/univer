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


class HandleJournalSerializer(serializers.ModelSerializer):
    """Закрыть/Открыть Журнал"""
    class Meta:
        model = sh_models.ElectronicJournal
        fields = (
            'uid',
            'closed',
        )

    def update(self, instance, validated_data):
        instance.closed = not instance.closed
        instance.save()

        return instance

