from django.urls import path
from . import apiviews

app_name = 'portal_users'

urlpatterns = [
    path('authenticate/', apiviews.LoginView.as_view(), name='auth'),
    path('forget/password/', apiviews.ForgetPasswordView.as_view(), name='forget-password'),
    path('reset/password/', apiviews.ResetPasswordView.as_view(), name='reset-password'),

    path('test/', apiviews.TestView.as_view(), name='test')
]
