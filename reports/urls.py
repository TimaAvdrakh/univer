from django.urls import path
from . import views

app_name = 'reports'


urlpatterns = [
    path('excel/reg_result/', views.RegisterResultExcelView.as_view(),
         name='reg_result_excel'),
    path('excel/reg_stat/', views.RegisterStatisticsExcelView.as_view(),
         name='reg_stat_excel'),

    path('excel/not_registered/', views.NotRegisteredStudentListExcelView.as_view(),
         name='not_registered_excel'),

    path('get_file/', views.GetFileView.as_view(),
         name='get_file'),
]
