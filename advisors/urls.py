from django.urls import path
from . import views

app_name = 'advisors'

urlpatterns = [
    path('register_bids/', views.RegistrationBidListView.as_view(), name='registration_bid_list'),
    path('short_disciplines/', views.DisciplineShortListView.as_view(), name='discipline_short_list'),
    path('acad_periods/', views.AcadPeriodListView.as_view(), name='acad_periods_for_filter'),
    path('faculties/', views.FacultyListView.as_view(), name='faculty_list'),
    path('cathedras/', views.CathedraListView.as_view(), name='cathedra_list'),
    path('edu_programs/', views.EducationProgramListView.as_view(), name='education_program_list'),
    path('edu_programs_group/', views.EducationProgramGroupListView.as_view(), name='education_program_group_list'),
    path('groups/', views.GroupListView.as_view(), name='groups'),

    path('check/student_choices/', views.CheckStudentChoices.as_view(), name='check_student_choices'),
]
