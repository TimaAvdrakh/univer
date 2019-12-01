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
from organizations.models import StudentDiscipline
from django.db.models import Max, Min
from portal.curr_settings import lesson_statuses
from django.utils.translation import gettext_lazy as _


class LoadType2Serializer(serializers.ModelSerializer):
    class Meta:
        model = LoadType2
        fields = (
            'uid',
            'name',
        )


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
    load_type = LoadType2Serializer()
    discipline = DisciplineSerializer()

    class Meta:
        model = models.ElectronicJournal
        fields = (
            'uid',
            'discipline',
            'load_type',
            'status',
            'flow_uid',
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

        student_count = StudentDiscipline.objects.filter(
            discipline=instance.discipline,
            load_type__load_type2=instance.load_type,
            teacher__in=instance.teachers.filter(is_active=True),
        ).distinct('student').count()

        data['student_nums'] = student_count

        data['lesson_start'] = lessons.aggregate(start=Min('date'))['start']
        data['lesson_end'] = lessons.aggregate(end=Max('date'))['end']

        executed_lesson_count = lessons.filter(status_id=lesson_statuses['executed']).count()
        lesson_count = lessons.count()
        data['lesson_count'] = '{}/{}'.format(executed_lesson_count,
                                              lesson_count)

        data['control_count'] = lessons.filter(intermediate_control=True).count()

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

        lesson.status_id = lesson_statuses['executed']
        lesson.save()

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



