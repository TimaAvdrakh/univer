from rest_framework import serializers
from . import models
from common.exceptions import CustomException
from datetime import datetime
from schedules import models as sh_models
from portal_users import models as user_models


class C1ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.C1Object
        fields = (
            'uid',
            'name',
            'model',
            'is_related',
        )


class C1ObjectCompareSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.C1ObjectCompare
        fields = (
            'uid',
            'name',
            'c1_object',
            'c1',
            'django',
            'main_field',
            'is_binary_data',
        )


class StudentPresenceSerializer(serializers.Serializer):
    auth_key = serializers.CharField()
    user = serializers.CharField(
        help_text='ИИН студента',
    )
    aud = serializers.UUIDField(
        help_text='Уид аудитории',
    )
    time = serializers.IntegerField(
        help_text='timestamp',
    )

    def save(self, **kwargs):
        cd = self.validated_data
        auth_key = cd.get('auth_key')
        iin = cd.get('user')
        aud_id = cd.get('aud')
        timestamp = cd.get('time')

        if auth_key != '123':
            raise CustomException(detail='auth_key_invalid')

        try:
            student = user_models.Profile.objects.get(iin=iin,
                                                      is_active=True)

        except user_models.Profile.DoesNotExist:
            raise CustomException(detail='student_not_found')

        dt_object = datetime.fromtimestamp(timestamp)
        date = dt_object.date()
        time = dt_object.time()

        try:
            lesson = sh_models.Lesson.objects.get(
                classroom_id=aud_id,
                date=date,
                time__from_time__lte=time,
                time__to_time__gte=time,
                is_active=True,
            )
        except sh_models.Lesson.DoesNotExist:
            raise CustomException(detail='lesson_not_found')

        try:
            sp = sh_models.StudentPerformance.objects.get(
                lesson=lesson,
                student=student,
                is_active=True,
            )
            sp.missed = False
            sp.save()
        except sh_models.StudentPerformance.DoesNotExist:
            sp = sh_models.StudentPerformance.objects.create(
                lesson=lesson,
                student=student,
                missed=False,
            )

        return sp
