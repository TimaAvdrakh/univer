"""portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_swagger.views import get_swagger_view
from applicant.viewsets import activate
from django.conf.urls.i18n import i18n_patterns


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
    path('api/v1/services/', include('services.urls', namespace='services')),

]

urlpatterns += [
    re_path(
        "activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/",
        activate,
        name='activate'
    )
]

# urlpatterns += i18n_patterns(
#
#     # prefix_default_language=False,
# )
