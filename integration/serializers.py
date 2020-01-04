from rest_framework import serializers
from portal_users import models as user_models
from common.exceptions import CustomException
from datetime import datetime
from schedules import models as sh_models
from .utils import timestamp_to_local_datetime


class StudentPresentListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        resp = []
        for item in validated_data:
            item_resp = {
                'data': item,
                'code': 0,
                'message': 'ok',
            }

            iin = item.get('user')
            aud_id = item.get('aud')
            timestamp = item.get('time')

            try:
                student = user_models.Profile.objects.get(iin=iin,
                                                          is_active=True)
            except user_models.Profile.DoesNotExist:
                item_resp['code'] = 1
                item_resp['message'] = 'student_not_found'
                resp.append(item_resp)

                continue

                # raise CustomException(detail='student_not_found',
                #                       status_code=404)

            # dt_object = datetime.fromtimestamp(timestamp)
            dt_object = timestamp_to_local_datetime(timestamp)
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
                item_resp['code'] = 2
                item_resp['message'] = 'lesson_not_found'
                resp.append(item_resp)

                continue

                # raise CustomException(detail='lesson_not_found',
                #                       status_code=404)

            try:
                sp = sh_models.StudentPerformance.objects.get(
                    lesson=lesson,
                    student=student,
                    is_active=True,
                )
                sp.missed = False
                sp.save()
            except sh_models.StudentPerformance.DoesNotExist:
                sh_models.StudentPerformance.objects.create(
                    lesson=lesson,
                    student=student,
                    missed=False,
                )

            resp.append(item_resp)

        self.resp = resp
        return resp


class StudentPresenceSerializer(serializers.Serializer):
    user = serializers.CharField(
        help_text='ИИН студента',
    )
    aud = serializers.UUIDField(
        help_text='Уид аудитории',
    )
    time = serializers.IntegerField(  # TODO Часовой пояс
        help_text='timestamp',
    )

    class Meta:
        list_serializer_class = StudentPresentListSerializer

