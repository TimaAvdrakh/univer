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

    path('my_discipline/', views.StudentDisciplineForRegListView.as_view(), name='my_disciplines_for_reg'),
    path('my_discipline/<pk>/edit/', views.ChooseTeacherView.as_view(), name='choose_teacher'),

    path('my_study_plans/', views.MyStudyPlanListView.as_view(), name='my_study_plans'),
    path('my_groups/', views.MyGroupListView.as_view(), name='my_group'),

    path('notify_advisor/', views.NotifyAdviser.as_view(), name='notify_advisor'),

    path('student/all_discipline/', views.StudentAllDisciplineListView.as_view(), name='students_all_discipline'),

    path('profile/<pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),

    path('profile/<pk>/contact/edit/', views.ContactEditView.as_view(), name='profile_contact_edit'),
    path('profile/<pk>/interests/edit/', views.InterestsEditView.as_view(), name='profile_interests_edit'),
    path('profile/<pk>/achievements/edit/', views.AchievementsEditView.as_view(), name='profile_achievements_edit'),

    path('avatar/upload/', views.AvatarUploadView.as_view(), name='avatar_upload'),

    path('my_roles/', views.RoleGetView.as_view(), name='my_roles'),
]
