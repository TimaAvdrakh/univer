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

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['url'] = CURRENT_API + '/schedules/?class_room={}'.format(instance.uid)
    #
    #     return data


class LessonSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer()
    groups = GroupShortSerializer(many=True)
    classroom = RoomSerializer()
    # time = TimeWindowSerializer()
    load_type = serializers.CharField()
    teachers = TeacherShortSerializer(many=True)

    class Meta:
        model = models.Lesson
        fields = (
            'uid',
            'discipline',
            'groups',
            'classroom',
            # 'time',
            'teachers',
            'load_type',
        )

