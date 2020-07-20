from django.urls import path
from . import views

app_name = 'instructions'

urlpatterns = [
    path('create/', views.CreateInstructionsVies.as_view(), name='create_instruction'),
    path('<name>/', views.UDRInstructionsView.as_view(), name='detail_instruction'),
    path('delete/<name>/', views.DestroyInstructions.as_view(), name='delete_instruction'),
    path('update/<name>/', views.UpdateInstructions.as_view(), name='update_instruction'),
]
