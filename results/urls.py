from django.urls import path

from results import views

urlpatterns = [
    path("myresult/",views.MyResults.as_view()),
    path("subjects/",views.Subjects.as_view()),
    path("exams/",views.Exams.as_view()),
    
    path(
        "families/<int:family_id>/students/",
        views.FamilyStudents.as_view()
    ),

    path(
        "students/<int:student_id>/enrollments/",
        views.StudentEnrollments.as_view()
    ),
    path(
        "enrollments/<int:enrollment_id>/results/",
        views.EnrollmentResults.as_view()
    ),

    path(
        "results/<int:result_id>/",
        views.ResultDetail.as_view()
    ),
    path(
        "families/<int:family_id>/promote/",
        views.PromoteStudents.as_view()
    ),
]