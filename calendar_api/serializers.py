import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Max
from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import *
from portal_users.models import (
    Profile,
    Role,
    RoleNames,
    RoleNamesRelated,
)
from schedules.models import (
    Room,
    RoomType,
    Lesson,
    LessonStudent,
    LessonTeacher,
)
from organizations.models import (
    StudyPlan
)
from portal_users.serializers import (
    ProfileLiteSerializer,
)
from common.serializers import (
    FileSerializer,
)


def convert_time(context):
    if context.get("event_start", None) is not None and context.get("event_end", None) is not None:
        event_start = "".join(context.get("event_start", None).rsplit(":", 1))
        event_start = datetime.datetime.strptime(event_start, '%Y-%m-%dT%H:%M:%S%z')
        event_start_range = event_start - datetime.timedelta(days=7)
        event_end = "".join(context.get("event_end", None).rsplit(":", 1))
        event_end = datetime.datetime.strptime(event_end, '%Y-%m-%dT%H:%M:%S%z')
        event_end_range = event_end + datetime.timedelta(days=7)
        return event_start, event_start_range, event_end, event_end_range


class EventsRepetitionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepetitionTypes
        fields = [
            'uid',
            'name',
            'code',
        ]


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = [
            'uid',
            'name',
        ]


class ReserveRoomSerializer(serializers.ModelSerializer):
    type = serializers.CharField()

    class Meta:
        model = Room
        fields = [
            'uid',
            'name',
            'type',
            'capacity',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        event_start, event_start_range, event_end, event_end_range = convert_time(self.context)
        events_queryset = Events.objects.filter(
            event_start__gte=event_start_range,
            event_end__lte=event_end_range,
            reserve_auditory=instance
        )
        data['events'] = EventLiteSerializer(events_queryset, many=True).data

        events_queryset = events_queryset.filter(
            Q(
                event_start__lt=event_end,
                event_end__gte=event_end,
            ) |
            Q(
                event_start__lte=event_start,
                event_end__gt=event_start,
            )
        )

        lessons = Lesson.objects.filter(
            date__gte=event_start_range.date(),
            date__lte=event_end_range.date(),
            classroom=instance,
        ).order_by('date', 'time')

        data['lessons'] = ScheduleSerializer(lessons, many=True).data

        # TODO Написать проверку совпадает ли событие с временем занятия если нужно

        if events_queryset.exists():
            data['reserved'] = True
        else:
            data['reserved'] = False
        return data


class EventParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participants
        fields = [
            'participant_profiles',
            'group',
            'faculty',
            'cathedra',
            'education_programs',
            'education_program_groups',
        ]


class EventSerializer(serializers.ModelSerializer):
    participants = EventParticipantsSerializer(required=False)
    files = FileSerializer(required=False, many=True)

    class Meta:
        model = Events
        fields = [
            'uid',
            'name',
            'event_start',
            'event_end',
            'event_place',
            'participants',
            'notification',
            'event_description',
            'reserve_auditory',
            'repetition_type',
            'files',
        ]

    def validate(self, validated_data):
        if validated_data.get('event_start', None) is None:
            raise ValidationError({"error": "start_date_is_empty"})
        elif validated_data.get('event_end', None) is None:
            raise ValidationError({"error": "end_date_is_empty"})
        elif validated_data['event_end'] <= validated_data['event_start']:
            raise ValidationError({"error": "must_be_greater"})
        elif validated_data.get('name', None) is None:
            raise ValidationError({"error": "name_is_empty"})
        return validated_data

    def create_participants(self, participants, exist_participants=None):
        participants_to_return = exist_participants
        if participants_to_return is not None:
            participants_to_return.participant_profiles.all().delete()
            participants_to_return.group.all().delete()
            participants_to_return.faculty.all().delete()
            participants_to_return.cathedra.all().delete()
            participants_to_return.education_programs.all().delete()
            participants_to_return.education_program_groups.all().delete()

        if exist_participants is None:
            participants_to_return = Participants.objects.create()
        if participants.get("participant_profiles", None) is not None:
            participants_to_return.participant_profiles.set(participants.get("participant_profiles"))
        if participants.get("group", None) is not None:
            participants_to_return.group.set(participants.get("group"))
        if participants.get("faculty", None) is not None:
            participants_to_return.faculty.set(participants.get("faculty"))
        if participants.get("cathedra", None) is not None:
            participants_to_return.cathedra.set(participants.get("cathedra"))
        if participants.get("education_programs", None) is not None:
            participants_to_return.education_programs.set(participants.get("education_programs"))
        if participants.get("education_program_groups", None) is not None:
            participants_to_return.education_program_groups.set(participants.get("education_program_groups"))
        participants_to_return.save()
        return participants_to_return

    def create(self, validated_data):
        creator = self.context['request'].user.profile
        participants = validated_data.get("participants", None)
        if participants is not None:
            participants = self.create_participants(participants)
        data = {
            'creator': creator,
            'participants': participants,
        }
        validated_data.update(data)
        event = Events.objects.create(**validated_data)
        event.save()
        return event

    def update(self, instance, validated_data):
        participants = validated_data.get("participants", None)
        data = {}
        if participants is not None:
            participants = self.create_participants(participants, instance.participants)
            data["participants"] = participants
        validated_data.update(data)
        instance.save()
        event = super().update(instance, validated_data)
        return event


class EventLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = [
            'uid',
            'event_start',
            'event_end',
            'name',
        ]


class SupervisorStudentsViewSerializer(serializers.ModelSerializer):
    group = serializers.CharField()
    faculty = serializers.CharField()
    cathedra = serializers.CharField()
    education_program = serializers.CharField()

    class Meta:
        model = StudyPlan
        fields = [
            'student',
            'group',
            'faculty',
            'cathedra',
            'education_program',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['full_name'] = instance.student.full_name
        return data


class ProfileAllEventsAndScheduleSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = [
            'uid',
            'full_name',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        study_plans = StudyPlan.objects.filter(student=instance).first()
        events = Events.objects.filter(participants__participant_profiles=instance)
        lookup = Q()
        if study_plans:
            lookup = Q(participants__group=study_plans.group)
            lookup |= Q(participants__faculty=study_plans.faculty)
            lookup |= Q(participants__cathedra=study_plans.cathedra)
            lookup |= Q(participants__education_programs=study_plans.education_programs)
            lookup |= Q(participants__education_program_groups=study_plans.education_programs.group)
            data['group'] = study_plans.group.name
            data['edu_program_group'] = study_plans.education_programs.group
        events = events.filter(lookup)
        data['events'] = EventLiteSerializer(events, many=True).data


class ProfilesEventsSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = [
            'uid',
            'full_name',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        event_start, event_start_range, event_end, event_end_range = convert_time(self.context)
        lookup = Q(
            participants__participant_profiles=instance,
            event_start__gte=event_start_range,
            event_end__lte=event_end_range,
        )

        study_plan = instance.studyplan_set.filter(student=instance).first()
        if study_plan:
            lookup = lookup | Q(participants__group=study_plan.group)
            lookup = lookup | Q(participants__faculty=study_plan.faculty)
            lookup = lookup | Q(participants__cathedra=study_plan.cathedra)
            lookup = lookup | Q(participants__education_programs=study_plan.education_program)
            lookup = lookup | Q(participants__education_program_groups=study_plan.education_program.group)

        profile_events = Events.objects.filter(lookup).distinct()

        profile_events_data = EventLiteSerializer(profile_events.order_by('event_start'), many=True).data
        data['events'] = profile_events_data

        lessons = []

        if instance.role.is_student:
            all_lessons = LessonStudent.objects.filter(student=instance).values_list('flow_uid')
            lessons = Lesson.objects.filter(
                flow_uid__in=all_lessons,
                date__gte=event_start_range.date(),
                date__lte=event_end_range.date(),
            ).order_by('date', 'time')

        if instance.role.is_teacher:
            lessons = Lesson.objects.filter(
                teachers=instance,
                date__gte=event_start_range.date(),
                date__lte=event_end_range.date(),
            ).order_by('date', 'time')

        data['lessons'] = ScheduleSerializer(lessons, many=True).data

        profile_events = profile_events.filter(
            Q(
                event_start__lt=event_end,
                event_end__gte=event_end,
            ) |
            Q(
                event_start__lte=event_start,
                event_end__gt=event_start,
            )
        ).distinct('pk')

        # TODO Написать проверку совпадает ли событие с временем занятия если нужно

        if profile_events.exists():
            data['profile_reserved'] = True
        else:
            data['profile_reserved'] = False

        return data


class GroupEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'uid',
            'name',
        ]


class CathedraEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cathedra
        fields = [
            'uid',
            'name',
        ]


class FacultyEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = [
            'uid',
            'name',
        ]


class EducationProgramEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationProgram
        fields = [
            'uid',
            'name',
        ]


class EducationProgramGroupEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationProgramGroup
        fields = [
            'uid',
            'name',
        ]


class RolenNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleNames
        fields = [
            'uid',
            'code',
            'name',
        ]


class ScheduleSerializer(serializers.ModelSerializer):
    discipline = serializers.CharField()
    classroom = serializers.CharField()
    time = serializers.CharField()
    status = serializers.CharField()
    language = serializers.CharField()
    teachers = ProfileLiteSerializer(many=True)

    class Meta:
        model = Lesson
        fields = [
            'uid',
            'date',
            'time',
            'discipline',
            'teachers',
            'classroom',
            'status',
            'subject',
            'language',
        ]
