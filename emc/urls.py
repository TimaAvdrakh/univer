from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'umk'

router = DefaultRouter()
router.register(r'emc', views.EMCModelViewSet, 'emc')
urlpatterns = router.urls

urlpatterns += [
    path('create', views.CreateTeacherEMC.as_view(), name='create_emc'),
    # path('list_th_one/<str:discipline>/', views.EMCListTeacherByDiscipline.as_view(),
    #      name='emc_list_teacher_by_discipline'),
]
