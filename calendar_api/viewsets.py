from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q, prefetch_related_objects
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet
from common.paginators import CustomPagination
from portal_users.models import Profile
from schedules.models import Room
from univer_admin.permissions import IsAdminOrReadOnly, AdminPermission
from . import models
from . import serializers


class EventsViewSet(ModelViewSet):
    queryset = models.Events.objects.all()
    serializer_class = serializers.EventSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def list(self, request):
        queryset = self.queryset.filter(creator=self.request.user.profile).order_by('event_start')
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True).data
        paginated_response = self.get_paginated_response(serializer)
        return Response(data=paginated_response.data, status=HTTP_200_OK)


class EventsRepetitionTypeViewSet(ModelViewSet):
    queryset = models.RepetitionTypes.objects.all()
    serializer_class = serializers.EventsRepetitionTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ReserveRoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = serializers.ReserveRoomSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def list(self, request):
        queryset = self.queryset
        event_start = request.query_params.get("event_start")
        event_end = request.query_params.get("event_end")
        if event_start is None or event_end is None:
            raise ValidationError({"error": "date_not_given"})
        events_query = models.Events.objects.filter(
            Q(
                event_start__lte=event_start,
                event_end__gte=event_end,
            ) |
            Q(
                event_start__lt=event_end,
                event_end__gte=event_end,
            ) |
            Q(
                event_start__lte=event_start,
                event_end__gt=event_start,
            ),
            reserve_auditory__isnull=False,
        ).values_list('reserve_auditory')
        if events_query.exists():
            queryset = queryset.exclude(pk__in=events_query).order_by('name')
        serializer_data = self.serializer_class(queryset, many=True).data
        return Response(data=serializer_data, status=HTTP_200_OK)
