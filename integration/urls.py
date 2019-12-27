from django.urls import path
from . import views

app_name = 'integration'


urlpatterns = [
    path('present_student/',
         views.StudentPresenceView.as_view(),
         name='present_student'),
]
