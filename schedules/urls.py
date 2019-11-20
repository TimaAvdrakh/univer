from django.urls import path
from . import views

app_name = 'schedules'


urlpatterns = [
    path('time_windows/', views.TimeWindowListView.as_view(), name='time_windows'),
    path('', views.ScheduleListView.as_view(), name='schedules'),
]