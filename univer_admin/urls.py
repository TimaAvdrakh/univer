from django.urls import path
from . import views

app_name = 'univer_admin'

urlpatterns = [
    path('lesson/<pk>/handle/',
         views.HandleLessonView.as_view(),
         name='lesson_handle'),

    path('journal/<pk>/handle/',
         views.HandleJournalView.as_view(),
         name='journal_handle'),

    path('lessons/',
         views.JournalLessonListView.as_view(),
         name='journal_lessons'),
]
