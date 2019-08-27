from django.urls import path
from . import views

app_name = 'portal_users'

urlpatterns = [
    path('login/', views.auth, name='login'),
]
