from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from . import viewsets

app_name = 'calendar_api'
router = DefaultRouter()
urlpatterns = router.urls