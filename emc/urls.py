from django.urls import path
from . import views

app_name = 'umk'

urlpatterns = [
    path('create', views.CreateTeacherEMC.as_view(), name='create_emc'),
    path('list_th_one', views.EMCListOneTeacher.as_view(), name='emc_list_one_teacher'),
    path('list_th_one/<str:discipline>/', views.EMCListTeacherByDiscipline.as_view(),
         name='emc_list_teacher_by_discipline'),
    path('list_st', views.ListStudentEMC.as_view(), name='list_student_emc'),
]
