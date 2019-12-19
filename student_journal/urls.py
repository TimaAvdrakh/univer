from django.urls import path
from . import views

app_name = 'student_journal'

urlpatterns = [
    path('my_performance/',
         views.MyPerformanceView.as_view(),
         name='my_performance'),

    path('my_performance/disc/',
         views.DisciplinePerformanceDetailView.as_view(),
         name='my_performance_disc'),
]
