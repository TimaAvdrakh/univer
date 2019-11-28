from rest_framework import serializers
from . import models
from organizations.serializers import DisciplineSerializer
from advisors.serializers import GroupShortSerializer
from portal_users.serializers import TeacherShortSerializer
from portal.local_settings import CURRENT_API
from portal_users.models import Profile
from common.exceptions import CustomException
import datetime
from organizations.models import LoadType2, AcadPeriod
from common.serializers import AcadPeriodSerializer


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


class ElectronicJournalDetailSerializer(serializers.ModelSerializer):
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lessons = instance.lessons.filter(is_active=True)
        if len(lessons) > 0:
            groups = lessons.first().groups.filter(is_active=True)

            serializer = GroupShortSerializer(groups,
                                              many=True)
            data['groups'] = serializer.data
        else:
            data['groups'] = []

        acad_period_pks = lessons.distinct('acad_period').values('acad_period')
        acad_periods = AcadPeriod.objects.filter(pk__in=acad_period_pks,
                                                 is_active=True)
        acad_period_serializer = AcadPeriodSerializer(acad_periods,
                                                      many=True)
        data['acad_periods'] = acad_period_serializer.data

        return data


class EvaluateSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(is_active=True),
    )
    lesson = serializers.PrimaryKeyRelatedField(
        queryset=models.Lesson.objects.filter(is_active=True),
    )
    mark = serializers.PrimaryKeyRelatedField(
        queryset=models.Mark.objects.filter(is_active=True),
        required=False,
    )
    missed = serializers.BooleanField(
        default=False,
        required=False,
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def save(self, **kwargs):
        lesson = self.validated_data.get('lesson')
        student = self.validated_data.get('student')
        mark = self.validated_data.get('mark')
        missed = self.validated_data.get('missed')
        reason = self.validated_data.get('reason')

        if datetime.date.today() < lesson.date:
            """Невозможно поставить оценку на будущее занятие"""
            raise CustomException()

        try:
            sp = models.StudentPerformance.objects.get(
                lesson=lesson,
                student=student,
                is_active=True,
            )

            if sp.mark and missed is True:
                """Запрещено поставить Н если оценка уже поставлена"""
                raise CustomException()
            elif sp.mark is None and missed is True:
                sp.missed = True
                sp.save()

            if mark and missed is False:
                sp.mark = mark
                sp.save()

        except models.StudentPerformance.DoesNotExist:
            if missed:
                sp = models.StudentPerformance.objects.create(
                    student=student,
                    lesson=lesson,
                    missed=True,
                    reason=reason,
                )
            else:
                sp = models.StudentPerformance.objects.create(
                    lesson=lesson,
                    student=student,
                    mark=mark,
                )

        return sp


class GradingSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GradingSystem
        fields = (
            'uid',
            'name',
            'number',
        )


class LessonUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lesson
        fields = (
            'uid',
            'subject',
            'grading_system',
        )

    def update(self, instance, validated_data):
        instance.subject = validated_data.get('subject')
        instance.grading_system = validated_data.get('grading_system')

        instance.save()
        return instance


class MarkSerializer(serializers.ModelSerializer):
    grading_system = serializers.CharField()

    class Meta:
        model = models.Mark
        fields = (
            'uid',
            'name',
            'grading_system',
            'value_number',
            'value_traditional',
        )


class ChooseControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lesson
        fields = (
            'uid',
            'intermediate_control',
        )

    def update(self, instance, validated_data):
        today = datetime.date.today()
        if today >= instance.date:
            raise CustomException()

        instance.intermediate_control = not instance.intermediate_control
        instance.save()

        return instance


class LessonShortSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer()
    groups = GroupShortSerializer(many=True)
    classroom = RoomSerializer()
    load_type = serializers.CharField()
    teachers = TeacherShortSerializer(many=True)
    time = TimeWindowSerializer()

    class Meta:
        model = models.Lesson
        fields = (
            'uid',
            'discipline',
            'date',
            'time',
            'groups',
            'classroom',
            'teachers',
            'load_type',
        )


class LoadType2Serializer(serializers.ModelSerializer):
    class Meta:
        model = LoadType2
        fields = (
            'uid',
            'name',
        )
