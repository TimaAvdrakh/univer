from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('acad_periods/', views.AcadPeriodListView.as_view(), name='acad_periods'),
    path('acad_periods_for_reg/', views.GetAcadPeriodsForRegisterView.as_view(),
         name='acad_periods_for_reg'),
    path('acad_periods_for_reg/copy/', views.GetAcadPeriodsForRegisterCopyView.as_view(),
         name='acad_periods_for_reg_copy'),

    path('levels/', views.LevelListView.as_view(), name='levels'),
    path('achievement_types/', views.AchievementTypeListView.as_view(), name='achievement_types'),

    path('study_years/', views.StudyYearListView.as_view(), name='study_years'),

    path('reg_periods/', views.RegistrationPeriodListView.as_view(), name='register_periods'),
    path('study_forms/', views.StudyFormListView.as_view(), name='study_forms'),

    path('test_status_codes/', views.TestStatusCodeView.as_view(), name='test_status_codes'),
    path('study_plan/study_years/', views.StudyYearFromStudyPlan.as_view(), name='study_years_from_study_plan'),
]

#123454