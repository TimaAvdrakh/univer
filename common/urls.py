from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('acad_periods/', views.AcadPeriodListView.as_view(), name='acad_periods'),
    path('acad_periods_for_reg/', views.GetAcadPeriodsForRegisterView.as_view(), name='acad_periods_for_reg'),

    path('levels/', views.LevelListView.as_view(), name='levels'),
    path('achievement_types/', views.AchievementTypeListView.as_view(), name='achievement_types'),

    path('study_years/', views.StudyYearListView.as_view(), name='study_years'),

    path('reg_periods/', views.RegistrationPeriodListView.as_view(), name='register_periods'),
]
