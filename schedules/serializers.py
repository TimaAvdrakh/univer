from rest_framework import serializers
from . import models
from organizations.serializers import DisciplineSerializer
from advisors.serializers import GroupShortSerializer
from portal_users.serializers import TeacherShortSerializer
from portal.local_settings import CURRENT_API


class TimeWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TimeWindow
        fields = (
            'uid',
            'from_time',
            'to_time',
        )


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Room
        fields = (
            'uid',
            'name',
            'capacity',
        )


class LessonSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer()
    groups = GroupShortSerializer(many=True)
    classroom = RoomSerializer()
    load_type = serializers.CharField()
    teachers = TeacherShortSerializer(many=True)

    class Meta:
        model = models.Lesson
        fields = (
            'uid',
            'discipline',
            'groups',
            'classroom',
            'teachers',
            'load_type',
        )


class ElectronicJournalSerializer(serializers.ModelSerializer):
    status = serializers.CharField()
    load_type = serializers.CharField()
    discipline = serializers.CharField()

    class Meta:
        model = models.ElectronicJournal
        fields = (
            'uid',
            'discipline',
            'load_type',
            'status',
        )
