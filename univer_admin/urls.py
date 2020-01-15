from django.urls import path
from . import views

app_name = 'univer_admin'

urlpatterns = [
    path('journals/',
         views.JournalListView.as_view(),
         name='journals'),

    path('lessons/',
         views.JournalLessonListView.as_view(),
         name='journal_lessons'),

    path('journal/handle/',
         views.HandleJournalView.as_view(),
         name='journal_handle'),

    path('lesson/handle/',
         views.HandleLessonView.as_view(),
         name='lesson_handle'),

    path('cathedras/',
         views.CathedraListView.as_view(),
         name='cathedras'),

    path('journal/cancel/plan_block/',
         views.CancelPlanBlockView.as_view(),
         name='cancel_plan_block'),
]

