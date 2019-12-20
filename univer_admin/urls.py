from django.urls import path
from . import views

app_name = 'univer_admin'

urlpatterns = [
    path('lesson/<pk>/allow_mark/',
         views.AllowMarkLessonView.as_view(),
         name='allow_mark'),

    path('journal/<pk>/handle/',
         views.HandleJournalView.as_view(),
         name='journal_handle'),
]