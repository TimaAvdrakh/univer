from rest_framework import serializers
from schedules import models as sh_models
from datetime import datetime, timedelta, date


class HandleLessonSerializer(serializers.ModelSerializer):
    """Открыть/закрыть выбранное занятие,"""

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
        if instance.closed:
            """Журнал закрыли"""
            instance.lessons.filter(is_active=True).update(closed=True,
                                                           admin_allow=False)
        else:
            """Журнал открыли, разблокируем его занятия на текущей неделе"""
            today = date.today()
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)

            instance.lessons.filter(
                is_active=True,
                date__gte=start_week,
                date__lte=end_week,
            ).update(admin_allow=True)

        instance.save()

        return instance
