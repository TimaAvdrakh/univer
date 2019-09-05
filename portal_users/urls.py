from django.urls import path
from . import views

app_name = 'portal_users'

urlpatterns = [
    path('authenticate/', views.LoginView.as_view(), name='auth'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('change/password/', views.PasswordChangeView.as_view(), name='change-password'),

    path('forget/password/', views.ForgetPasswordView.as_view(), name='forget-password'),
    path('reset/password/', views.ResetPasswordView.as_view(), name='reset-password'),

    path('jsdgfkjkc[wfefewfefewfwef/register/', views.UserRegisterView.as_view(), name='user_register'),

    path('test/', views.TestView.as_view(), name='test'),

    path('my_discipline/', views.StudentDisciplineListView.as_view(), name='my_disciplines'),
    path('my_study_plan/', views.StudyPlanDetailView.as_view(), name='my_study_plan'),
    path('my_discipline/<pk>/edit/', views.ChooseTeacherView.as_view(), name='choose_teacher'),
]
