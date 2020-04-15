from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Дипломная работа
    path('type/', views.TypeView.as_view(), name='type'),
    path('subtype/', views.SubTypeView.as_view(), name='subtype')
]
