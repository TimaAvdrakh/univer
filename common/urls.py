from django.urls import path
from . import views

app_name = 'portal_users'

urlpatterns = [
    path('acad_periods/', views.AcadPeriodList.as_view(), name='acad_periods'),
]
