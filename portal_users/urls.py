from django.urls import path
from . import views

app_name = 'portal_users'

urlpatterns = [
    path('authenticate/', views.LoginView.as_view(), name='login'),
]
