from django.urls import path
from . import views

app_name = 'schedules'


urlpatterns = [
    path('time_windows/', views.TimeWindowListView.as_view(), name='time_windows'),
    path('groups/', views.GroupListView.as_view(), name='groups'),
    path('disciplines/', views.DisciplineListView.as_view(), name='disciplines'),
    path('teachers/', views.TeacherListView.as_view(), name='teachers'),
    path('class_rooms/', views.ClassRoomListView.as_view(), name='class_rooms'),

    path('', views.ScheduleListView.as_view(), name='schedules'),
]