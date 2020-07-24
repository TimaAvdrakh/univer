from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'umk'

router = DefaultRouter()
router.register(r'emc', views.EMCModelViewSet, 'emc')
urlpatterns = router.urls

urlpatterns += [
    path('create', views.CreateTeacherEMC.as_view(), name='create_emc'),
]
