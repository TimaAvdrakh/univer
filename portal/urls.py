from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Univer API')

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('korabolta/', admin.site.urls),
    path('api/swagger/6456afdsfdsgfsdg/', schema_view),
    path('api/v1/user/', include('portal_users.urls', namespace="user")),
    path('api/v1/common/', include('common.urls', namespace="common")),
    path('api/v1/advisors/', include('advisors.urls', namespace='advisors')),
    path('api/v1/reports/', include('reports.urls', namespace='reports')),
    path('api/v1/schedules/', include('schedules.urls', namespace='schedules')),
    path('api/v1/c1/', include('c1.urls', namespace='c1')),
    path('api/v1/admin/', include('univer_admin.urls', namespace='univer_admin')),

    path('api/v1/stud_jour/', include('student_journal.urls', namespace='student_journal')),
    path('api/v1/integration/', include('integration.urls', namespace='integration')),
    path('api/v1/applicant/', include('applicant.urls', namespace='applicant')),
    path('api/v1/organizations/', include('organizations.urls', namespace='organizations')),
    path('api/v1/applications/', include('applications.urls', namespace='applications')),
    path('api/v1/calendar/', include('calendar_api.urls', namespace='calendar_api')),

]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
