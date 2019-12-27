from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'c1'

urlpatterns = [
    path('putfrom1c/', views.putfrom1c, name='putfrom1c'),

    path('c1_objects/', views.C1ObjectView.as_view(), name='C1Objects'),
    path('c1_object_compares/', views.C1ObjectCompareView.as_view(), name='c1_object_compares'),
    path('copy_rules/', views.CopyRuleView.as_view(), name='copy_rules'),

    path('load/avatars/', views.LoadAvatarView.as_view(), name='load_avatars'),
    # path('delete_all/', views.DelAllView.as_view(), name='delete_all'),

    # url('^putpicturefrom1c/$', views.putpicturefrom1c, name='putpicturefrom1c'),
    # url('^putactfrom1c/$', views.putactfrom1c, name='putactfrom1c'),
    # url('^putcountfrom1c/$', views.putcountfrom1c, name='putcountfrom1c'),
    # url('^putfilefrom1c/$', views.putfilefrom1c, name='putfilefrom1c'),
    # url('^get1corders/$', views.get1corders, name='get1corders'),
    # url('^get1cpreorders/$', views.get1cpreorders, name='get1cpreorders'),
    # url('^get1caddress/$', views.get_delivery_addresses, name='get1caddress'),
    # url('^complete1corders/$', views.complete1corders, name='complete1corders'),
    # url('^clear_123_cache/$', views.clear_cache, name='clear_123_cache'),
    # url('^login1c/$', views.logon1c, name="logon1c")
]
