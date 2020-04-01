from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = "portal_users"

urlpatterns = [
    path('authenticate/', views.LoginView.as_view(), name='auth'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('change/password/', views.PasswordChangeView.as_view(), name='change-password'),

    path('forget/password/', views.ForgetPasswordView.as_view(), name='forget-password'),
    path('reset/password/', views.ResetPasswordView.as_view(), name='reset-password'),

    path('jsdgfkjkc[wfefewfefewfwef/register/', views.UserRegisterView.as_view(), name='user_register'),

    path('test/', views.TestView.as_view(), name='test'),

    path('my_discipline/', views.StudentDisciplineForRegListView.as_view(), name='my_disciplines_for_reg'),
    path('my_discipline/copy/',
         views.StudentDisciplineForRegListCopyView.as_view(),
         name='my_disciplines_for_reg_copy'),

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

    path('my_discipline/control_forms/', views.ChooseControlFormListView.as_view(),
         name='discipline_control_forms'),
    path('control_forms/<pk>/choose/', views.ChooseFormControlView.as_view(),
         name='choose_control_forms'),
    path('student_status/', views.StudentStatusListView.as_view(),
         name='student_status'),
    path('gender/', views.GenderListView.as_view(),
         name='gender'),
    path('citizenship/', views.CitizenshipListView.as_view(),
         name='citizenship')
]

router = DefaultRouter()
router.register(r"genders", views.GenderViewSet)
router.register(r"marital-statuses", views.MaritalStatusViewSet)
router.register(r"phone-types", views.PhoneTypeViewSet)
urlpatterns += router.urls
