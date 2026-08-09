from django.db import models

from users.models import CustomUser

# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=100)
    final_grade = models.IntegerField()
    success_grade = models.IntegerField()

    def __str__(self):
        return self.name

class Exam(models.Model):
    name = models.CharField(max_length=100)
    year = models.CharField(max_length=20)

    def __str__(self):
        return self.name
        
class StudentEnrollment(models.Model):
    STATUS_CHOICES = [
        ("ناجح", "ناجح"),
        ("راسب", "راسب"),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    family = models.ForeignKey("stages.Family", on_delete=models.PROTECT,related_name="enrollments")
    academic_year = models.CharField(max_length=20)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'family', 'academic_year'], name='unique_student_family_academic_year')
        ]

    def __str__(self):
        return (
            f"{self.student.full_name} - "
            f"{self.family.name} - "
            f"{self.academic_year}"
        )

class Result(models.Model):
    enrollment = models.ForeignKey(
        StudentEnrollment,
        on_delete=models.CASCADE,
        related_name="results"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    points = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "enrollment",
                    "subject",
                    "exam",
                ],
                name="unique_result_per_enrollment_subject_exam"
            )
        ]

    def __str__(self):
        return self.enrollment.student.full_name

    def is_success(self):
        return self.points >= self.subject.success_grade

    