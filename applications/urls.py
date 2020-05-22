from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from . import views

app_name = 'applications'

urlpatterns = [
    path('type/', views.TypeView.as_view(), name='type'),
    path('subtype/', views.SubTypeView.as_view(), name='subtype'),

    path('application/', views.ApplicationView.as_view(), name='subtype'),

    # файлы
    re_path(r'^media/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT, }),
]
