from django.urls import path
from . import views

app_name = 'portal_users'

urlpatterns = [
    path('authenticate/', views.LoginView.as_view(), name='auth'),
    path('forget/password/', views.ForgetPasswordView.as_view(), name='forget-password'),
    path('reset/password/', views.ResetPasswordView.as_view(), name='reset-password'),

    path('test/', views.TestView.as_view(), name='test')
]
