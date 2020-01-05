from rest_framework import serializers
from schedules import models as sh_models
from datetime import datetime, timedelta, date
from cron_app.models import PlanCloseJournalTask
from django.utils import timezone
from common.exceptions import CustomException


class HandleLessonSerializer(serializers.Serializer):
    """Открыть/закрыть выбранные занятия,"""
    lessons = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=sh_models.Lesson.objects.filter(is_active=True),
        )
    )

    def save(self, **kwargs):
        lessons = self.validated_data.get('lessons')
        for lesson in lessons:
            lesson.admin_allow = not lesson.admin_allow
            lesson.save()

        return lessons


class HandleJournalSerializer(serializers.Serializer):
    """Закрыть/Открыть Журналы"""
    journals = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=sh_models.ElectronicJournal.objects.filter(is_active=True),
        )
    )
    date_time = serializers.DateTimeField(required=False,
                                          allow_null=True)

    def save(self, **kwargs):
        journals = self.validated_data.get('journals')
        date_time = self.validated_data.get('date_time')

        if date_time:
            '''Закроем журналы в указанное время'''

            now = datetime.now()
            if date_time <= now:
                """Запретим прошедшее время"""
                raise CustomException(detail='past_date_time')

            task = PlanCloseJournalTask.objects.create(
                date_time=date_time,
            )
            task.journals.set(journals)
            for journal in journals:
                journal.plan_block_date = date_time
                journal.save()
        else:
            '''Закроем журналы сейчас'''
            for journal in journals:
                journal.closed = not journal.closed
                if journal.closed:
                    """Журнал закрыли"""
                    journal.block_date = datetime.now()
                    journal.close_lessons()
                else:
                    """Журнал открыли, разблокируем его занятия на текущей неделе"""
                    today = date.today()
                    start_week = today - timedelta(days=today.weekday())
                    end_week = start_week + timedelta(days=6)

                    journal.lessons.filter(
                        is_active=True,
                        date__gte=start_week,
                        date__lte=end_week,
                    ).update(admin_allow=True)

                journal.save()

        return journals
