from django.urls import path

from attendance import views

urlpatterns = [
    path("myattendance/",views.StudentAttendanceView.as_view()),
]