from rest_framework import serializers
from . import models
from common.exceptions import CustomException


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Type
        fields = (
            'uid',
            'name',
        )

class SubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubType
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
        model = models.Application
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        #sub_application = models.SubApplication.objects.filter(application=instance.id)
        sub_application = models.SubApplication.objects.filter(application=instance.id)
        sub_application_serializer = SubApplicationSerializer(instance=sub_application, many=True)
        data['sub_application'] = sub_application_serializer.data
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        if user and user.is_authenticated:
            application: Application = super().create(validated_data)
            #application.form = user.questionnaires.first()
            #application.status = ApplicationStatus.objects.get(code=WAITING_VERIFY)
            #application.form.save()
            return application
        else:
            raise ValidationError({"error": "user undefined"})


class SubApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubApplication
        fields = "__all__"