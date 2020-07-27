from django.urls import path
from . import views

app_name = 'instructions'

urlpatterns = [
    path('create/', views.CreateInstructionsVies.as_view(), name='create_instruction'),
    path('<name>/', views.InstructionsView.as_view(), name='detail_instruction'),
]
