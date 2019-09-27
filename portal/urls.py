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
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from django.conf.urls.i18n import i18n_patterns

schema_view = get_swagger_view(title='Univer API')

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('korabolta/', admin.site.urls),
    path('api/swagger/6456afdsfdsgfsdg/', schema_view),
    path('api/v1/user/', include('portal_users.urls', namespace="user")),
    path('api/v1/common/', include('common.urls', namespace="common")),
    path('api/v1/advisors/', include('advisors.urls', namespace='advisors')),
]

# urlpatterns += i18n_patterns(
#
#     # prefix_default_language=False,
# )
