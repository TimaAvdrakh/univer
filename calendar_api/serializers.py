import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Max
from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import *
from portal_users.models import Profile, Role
from schedules.models import (
    Room,
    RoomType,
)
from organizations.models import (
    StudyPlan
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
        model = models.RepetitionTypes
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

    def create_participants(self, participants):
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
        participants = validated_data.pop("participants")
        if len(participants) == 0:
            participants = Profile.objects.none()
        else:
            instance.participants.all().delete()
        instance.participants.set(participants)
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
        ]


class ProfilesEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyPlan
        fields = [
            'student',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['full_name'] = f"{instance.student.first_name} {instance.student.last_name} {instance.student.middle_name}"
        event_start, event_start_range, event_end, event_end_range = convert_time(self.context)
        profile_events = Events.objects.filter(
            Q(participants__participant_profiles=instance.student)|
            Q(participants__group=instance.group)|
            Q(participants__faculty=instance.faculty)|
            Q(participants__cathedra=instance.cathedra)|
            Q(participants__education_programs=instance.education_program),
            event_start__gte=event_start_range,
            event_end__lte=event_end_range,
        ).distinct('pk')
        profile_events_data = EventLiteSerializer(profile_events.order_by('pk'), many=True).data
        data['events'] = profile_events_data
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