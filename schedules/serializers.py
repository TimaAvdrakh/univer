from rest_framework import serializers
from . import models
from organizations.serializers import DisciplineSerializer
from advisors.serializers import GroupShortSerializer
from portal_users.serializers import TeacherShortSerializer
from portal.local_settings import CURRENT_API
from portal_users.models import Profile


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


class EvaluateSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(is_active=True),
    )
    lesson = serializers.PrimaryKeyRelatedField(
        queryset=models.Lesson.objects.filter(is_active=True),
    )
    mark = serializers.CharField(
        required=False,
        allow_blank=True,
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
        mark_value = self.validated_data.get('mark')
        missed = self.validated_data.get('missed')
        reason = self.validated_data.get('reason')

        performances = models.StudentPerformance.objects.filter(
            lesson=lesson,
            student=student,
            is_active=True,
        )

        if performances.exists():
            try:
                sp = performances.get(mark__grading_system=lesson.grading_system)

                if missed:
                    sp.missed = True
                    sp.mark = None
                    sp.save()
                else:
                    mark = sp.mark
                    mark.value_number = mark_value
                    # mark.weight =
                    # mark.value_letter =   TODO
                    # mark.value_traditional =
                    mark.save()

            except models.StudentPerformance.DoesNotExist:
                # TODO N
                try:
                    sp = performances.get(missed=True)
                except models.StudentPerformance.DoesNotExist:
                    pass

                # if missed:
                #     models.StudentPerformance.objects.create(
                #         student=student,
                #         lesson=lesson,
                #         missed=True,
                #         reason=reason,
                #     )
                # else:
                #     mark = models.Mark.objects.create(
                #         weight=45,
                #         grading_system=lesson.grading_system,
                #         value_letter='A',
                #         value_number=mark_value,
                #         value_traditional='Хорошо',
                #     )
                #     sp = models.StudentPerformance.objects.create(
                #         lesson=lesson,
                #         student=student,
                #         mark=mark,
                #     )
        else:
            if missed:
                models.StudentPerformance.objects.create(
                    student=student,
                    lesson=lesson,
                    missed=True,
                    reason=reason,
                )
            else:
                mark = models.Mark.objects.create(
                    weight=45,
                    grading_system=lesson.grading_system,
                    value_letter='A',
                    value_number=mark_value,
                    value_traditional='Хорошо',
                )
                sp = models.StudentPerformance.objects.create(
                    lesson=lesson,
                    student=student,
                    mark=mark,
                )


class GradingSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GradingSystem
        fields = (
            'uid',
            'name',
            'code',
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

