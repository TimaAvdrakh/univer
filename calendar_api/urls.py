from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from . import viewsets

app_name = 'calendar_api'
router = DefaultRouter()
router.register(r"events", viewsets.EventsViewSet, "events")
router.register(r"events_repetition_types", viewsets.EventsRepetitionTypeViewSet, "events_repetition_types")
router.register(r"reserve_rooms", viewsets.ReserveRoomViewSet, "reserve_rooms")
urlpatterns = router.urls
