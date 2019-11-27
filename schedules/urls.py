from django.urls import path
from . import views

app_name = 'schedules'


urlpatterns = [
    # Schedules
    path('time_windows/', views.TimeWindowListView.as_view(), name='time_windows'),
    path('groups/', views.GroupListView.as_view(), name='groups'),
    path('disciplines/', views.DisciplineListView.as_view(), name='disciplines'),
    path('teachers/', views.TeacherListView.as_view(), name='teachers'),
    path('class_rooms/', views.ClassRoomListView.as_view(), name='class_rooms'),

    path('', views.ScheduleListView.as_view(), name='schedules'),

    # Electronic Journal
    path('journals/', views.ElJournalListView.as_view(), name='journals'),
    path('journal/', views.JournalDetailView.as_view(), name='journal_detail'),

    path('performance/', views.StudentPerformanceView.as_view(), name='performance'),

    path('lesson/grading_system/', views.GetGradingSystemView.as_view(), name='grading_system'),
    path('evaluate/', views.EvaluateView.as_view(), name='evaluate'),

    path('grading_systems/', views.GradingSystemListView.as_view(), name='grading_systems'),

    path('lesson/<pk>/edit/', views.ChangeLessonView.as_view(), name='change_lesson'),

    path('marks/', views.MarkListView.as_view(), name='marks'),
]

