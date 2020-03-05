from django.urls import path
from . import views

app_name = 'advisors'

urlpatterns = [
    # 1 стр Заявки на ИУПы обучающихся
    path('study_plans/', views.StudyPlansListView.as_view(),  # Не используется
         name='registration_bid_list'),
    path('study_plans/copy/', views.CopyStudyPlansListView.as_view(),
         name='registration_bid_list_copy'),

    path('student/disciplines/', views.StudentDisciplineListView.as_view(), name='discipline_short_list'),
    path('student/disciplines/grouped/', views.StudentDisciplineGroupListView.as_view(),
         name='student_discipline_group_list'),

    path('acad_periods/', views.AcadPeriodListView.as_view(), name='acad_periods_for_filter'),
    path('faculties/', views.FacultyListView.as_view(), name='faculty_list'),
    path('cathedras/', views.CathedraListView.as_view(), name='cathedra_list'),
    path('edu_programs/', views.EducationProgramListView.as_view(), name='education_program_list'),
    path('edu_programs_group/', views.EducationProgramGroupListView.as_view(), name='education_program_group_list'),
    path('groups/', views.GroupListView.as_view(), name='groups'),

    path('check/student_choices/', views.CheckStudentChoices.as_view(), name='check_student_choices'),

    # 2 стр ИУПы обучающихся
    path('student/study_plan/', views.GetStudyPlanView.as_view(), name='student_study_plan'),
    path('students/', views.FilteredStudentsListView.as_view(), name='students'),
    path('speciality/', views.SpecialityListView.as_view(), name='speciality_list'),
    path('student/confirmed/disciplines/', views.ConfirmedStudentDisciplineListView.as_view(),  # TODO TEST order_by
         name='confirmed_disciplines'),

    # 3 стр
    path('registration/results/', views.RegisterResultView.as_view(),  # TODO order_by
         name='registration_results'),

    path('registration/statistics/', views.RegisterStatisticsView.as_view(),  # TODO order_by
         name='registration_statistics'),

    path('not_registered/students/', views.NotRegisteredStudentListView.as_view(),  # TODO order_by
         name='not_registered_students'),

    # Excel views
    path('excel/', views.GenerateIupBidExcelView.as_view(),
         name='generate_excel'),

    path('iup_excel/', views.GenerateIupExcelView.as_view(),
         name='generate_iup_excel'),

    path('discipline/<pk>/deactivate/', views.DeactivateDiscipline.as_view(),
         name='deactivate_discipline'),

    path('discipline/<pk>/activate/', views.ActivateDiscipline.as_view(), name='activate_discipline'),

    # 4 стр Список учащихся
    path('students/all/', views.StudentProfilesList.as_view(),
         name='student_profiles'),

]
