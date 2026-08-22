from django.urls import path

from results import views

from results import views

urlpatterns = [
    path("myresult/", views.MyResults.as_view()),

    path("subjects/", views.Subjects.as_view()),
    path("subjects/<int:subject_id>/", views.SubjectDetail.as_view()),

    path("exams/", views.Exams.as_view()),
    path("exams/<int:exam_id>/", views.ExamDetail.as_view()),

    path("subject-exams/", views.SubjectExams.as_view()),
    path("subject-exams/<int:subject_exam_id>/", views.SubjectExamDetail.as_view()),

    path("families/", views.ResultFamilies.as_view()),
    path("families/<int:family_id>/students/", views.FamilyStudents.as_view()),
    path("students/<int:student_id>/enrollments/", views.StudentEnrollments.as_view()),
    path("enrollments/<int:enrollment_id>/results/", views.EnrollmentResults.as_view()),
    path("results/<int:result_id>/", views.ResultDetail.as_view()),
    path("families/<int:family_id>/promote/", views.PromoteStudents.as_view()),
]