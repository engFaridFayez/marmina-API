from django.urls import path

from results import views

urlpatterns = [
    path("myresult/",views.MyResults.as_view()),
    path("subjects/",views.Subjects.as_view()),
    path("exams/",views.Exams.as_view()),
]