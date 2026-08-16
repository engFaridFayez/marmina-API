from django.db import models
from django.core.exceptions import ValidationError
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
    
class SubjectExam(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="subject_exams"
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    max_grade = models.IntegerField()
    success_grade = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "exam"],
                name="unique_subject_exam"
            )
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.exam.name}"

##############################################
#             مزامير الاجبية
##############################################
class SubjectComponent(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="components"
    )

    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class ComponentExam(models.Model):
    component = models.ForeignKey(
        SubjectComponent,
        on_delete=models.CASCADE,
        related_name="component_exams"
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    max_grade = models.IntegerField()
    success_grade = models.IntegerField(null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["component", "exam"],
                name="unique_component_exam"
            )
        ]

    def __str__(self):
        return f"{self.component} - {self.exam.name}"


##############################################
#             مزامير الاجبية    /
##############################################












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

    subject_exam = models.ForeignKey(
        SubjectExam,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    component_exam = models.ForeignKey(
        ComponentExam,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    points = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "enrollment",
                    "subject_exam",
                ],
                name="unique_subject_result"
            ),
            models.UniqueConstraint(
                fields=[
                    "enrollment",
                    "component_exam",
                ],
                name="unique_component_result"
            ),
        ]

    def __str__(self):
        return self.enrollment.student.full_name

    def is_success(self):
        if self.subject_exam:
            return self.points >= self.subject_exam.success_grade

        if self.component_exam:
            return None

        return None

        return True
    def clean(self):
        if bool(self.subject_exam) == bool(self.component_exam):
            raise ValidationError(
                "Result must have either subject_exam or component_exam."
            )