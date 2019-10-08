from django.urls import path
from . import views

app_name = 'advisors'

urlpatterns = [
    path('study_plans/', views.StudyPlansListView.as_view(), name='registration_bid_list'),
    path('student/disciplines/', views.StudentDisciplineListView.as_view(), name='discipline_short_list'),
    path('acad_periods/', views.AcadPeriodListView.as_view(), name='acad_periods_for_filter'),
    path('faculties/', views.FacultyListView.as_view(), name='faculty_list'),
    path('cathedras/', views.CathedraListView.as_view(), name='cathedra_list'),
    path('edu_programs/', views.EducationProgramListView.as_view(), name='education_program_list'),
    path('edu_programs_group/', views.EducationProgramGroupListView.as_view(), name='education_program_group_list'),
    path('groups/', views.GroupListView.as_view(), name='groups'),

    path('check/student_choices/', views.CheckStudentChoices.as_view(), name='check_student_choices'),

    path('student/study_plan/', views.GetStudyPlanView.as_view(), name='student_study_plan'),
    path('students/', views.FilteredStudentsListView.as_view(), name='students'),
    path('student/confirmed/disciplines/', views.ConfirmedStudentDisciplineListView.as_view(),
         name='confirmed_disciplines'),

    path('confirmed/acad_periods/', views.ConfirmedAcadPeriodListView.as_view(),
         name='confirmed_acad_periods_for_filter'),
]
