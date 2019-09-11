from django.urls import path
from . import views

app_name = 'portal_users'

urlpatterns = [
    path('acad_periods/', views.AcadPeriodList.as_view(), name='acad_periods'),
    path('acad_periods_for_reg/', views.GetAcadPeriodsForRegister.as_view(), name='acad_periods_for_reg'),

]
