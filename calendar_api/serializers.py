from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Max
from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from . import models
from portal_users.models import Profile, Role


class EventsRepetitionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RepetitionTypes
        fields = [
            'uid',
            'name',
            'code',
        ]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Events
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

    def create(self, validated_data):
        creator = self.context['request'].user.profile
        data = {
            'creator': creator,
        }
        validated_data.update(data)
        participants = validated_data.pop("participants")
        event = models.Events.objects.create(**validated_data)
        if len(participants) == 0:
            participants = Profile.objects.none()
        event.participants.set(participants)
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




