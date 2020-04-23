from rest_framework import serializers
from .models import *
from rest_framework.validators import ValidationError

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = (
            'uid',
            'name',
        )

class SubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubType
        fields = (
            'uid',
            'name',
            'type',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['example_file'] = instance.example.file.url
        return data

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        #sub_application = SubApplication.objects.filter(application=instance.id)
        sub_application = SubApplication.objects.filter(application=instance.id)
        sub_application_serializer = SubApplicationSerializer(instance=sub_application, many=True)
        data['sub_application'] = sub_application_serializer.data
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        if user and user.is_authenticated:


            application :Application = super().create(validated_data)
            # application = Application.objects.create(**validated_data)

            # application.status = Status.objects.get(c1_id="1").uid
            # application.profile = user.profile.uid
            # application.type = application.type.uid

            return application
        else:
            raise ValidationError({"error": "user undefined"})


class SubApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubApplication
        fields = "__all__"