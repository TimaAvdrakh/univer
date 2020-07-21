from django.urls import path
from . import views

app_name = 'umk'

urlpatterns = [
    path('create', views.CreateEMC.as_view(), name='create_emc'),
    path('list', views.ListEMC.as_view(), name='list_emc'),
]
